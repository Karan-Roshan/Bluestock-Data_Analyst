from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "nifty100.db"
RAW = ROOT / "data" / "raw" / "market_cap.xlsx"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)


def _read_raw():
    """Read market_cap.xlsx with automatic header detection."""
    if not RAW.exists():
        raise FileNotFoundError(f"Missing {RAW}")

    raw = pd.read_excel(RAW, header=None)
    required = {"company_id", "year"}
    header_row = None

    for i in range(min(len(raw), 15)):
        vals = {str(v).strip().lower() for v in raw.iloc[i].dropna().tolist()}
        if required.issubset(vals):
            header_row = i
            break

    if header_row is None:
        # Current project files normally have the real header on row 0.
        # Keep a useful error instead of failing later with KeyError.
        raise ValueError(
            "Could not find market_cap.xlsx header containing company_id and year"
        )

    x = pd.read_excel(RAW, header=header_row)
    x.columns = [str(c).strip() for c in x.columns]

    # Normalize the source names used by the valuation module.
    aliases = {
        "id": "row_id",
        "market_cap_crore": "market_cap",
    }
    x = x.rename(columns=aliases)

    required_cols = {"company_id", "year", "market_cap", "pe_ratio", "pb_ratio", "ev_ebitda"}
    missing = required_cols - set(x.columns)
    if missing:
        raise ValueError(
            f"market_cap.xlsx is missing required columns: {sorted(missing)}"
        )

    x["year_num"] = pd.to_numeric(x["year"], errors="coerce")
    return x


def build_valuation():
    x = _read_raw()

    with sqlite3.connect(DB) as con:
        comp = pd.read_sql_query(
            "SELECT company_id, company_name, broad_sector FROM companies", con
        )
        cf = pd.read_sql_query(
            "SELECT company_id, period, cash_from_operating, cash_from_investing "
            "FROM cashflow",
            con,
        )

    # Latest market-cap/valuation observation for every company.
    latest = (
        x.dropna(subset=["company_id", "year_num"])
         .sort_values(["company_id", "year_num"])
         .groupby("company_id", as_index=False)
         .tail(1)
         .copy()
    )

    latest = latest.merge(comp, on="company_id", how="left")

    # FCF = CFO + CFI, using the existing Sprint-1/2 SQLite column names.
    cf["fcf"] = (
        pd.to_numeric(cf["cash_from_operating"], errors="coerce")
        + pd.to_numeric(cf["cash_from_investing"], errors="coerce")
    )
    cf["period_num"] = pd.to_numeric(cf["period"], errors="coerce")

    fcf = (
        cf.dropna(subset=["company_id", "period_num"])
          .sort_values(["company_id", "period_num"])
          .groupby("company_id", as_index=False)
          .tail(1)[["company_id", "fcf"]]
    )
    latest = latest.merge(fcf, on="company_id", how="left")

    latest["fcf_yield_pct"] = (
        pd.to_numeric(latest["fcf"], errors="coerce")
        / pd.to_numeric(latest["market_cap"], errors="coerce")
        * 100
    )

    latest["pe_ratio"] = pd.to_numeric(latest["pe_ratio"], errors="coerce")
    latest["pb_ratio"] = pd.to_numeric(latest["pb_ratio"], errors="coerce")
    latest["ev_ebitda"] = pd.to_numeric(latest["ev_ebitda"], errors="coerce")

    # Sprint 4 asks for the sector median P/E in the latest year.
    latest["5yr_median_PE"] = latest.groupby("broad_sector")["pe_ratio"].transform(
        "median"
    )

    latest["PE_vs_sector_median_pct"] = (
        latest["pe_ratio"] / latest["5yr_median_PE"] - 1
    ) * 100

    latest["flag"] = np.select(
        [
            latest["pe_ratio"] > latest["5yr_median_PE"] * 1.5,
            latest["pe_ratio"] < latest["5yr_median_PE"] * 0.7,
        ],
        ["Caution", "Discount"],
        default="Fair",
    )

    latest = latest.rename(
        columns={
            "broad_sector": "sector",
            "pe_ratio": "P/E",
            "pb_ratio": "P/B",
            "ev_ebitda": "EV/EBITDA",
        }
    )

    out = latest[
        [
            "company_id",
            "company_name",
            "sector",
            "P/E",
            "P/B",
            "EV/EBITDA",
            "fcf_yield_pct",
            "5yr_median_PE",
            "PE_vs_sector_median_pct",
            "flag",
        ]
    ].copy()

    # Keep exactly one row per company in the requested 92-company universe.
    out = out.drop_duplicates(subset=["company_id"], keep="last")

    out.to_excel(OUT / "valuation_summary.xlsx", index=False)
    out[out["flag"].isin(["Caution", "Discount"])].to_csv(
        OUT / "valuation_flags.csv", index=False
    )

    return out


if __name__ == "__main__":
    out = build_valuation()
    print(f"Valuation rows: {len(out)}")
    print(out["flag"].value_counts(dropna=False).to_string())
