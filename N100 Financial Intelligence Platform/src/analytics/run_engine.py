"""Calculate Sprint 2 ratios from the actual loaded company data."""

from pathlib import Path
import sqlite3
import math
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "nifty100.db"
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)


def safe_div(a, b):
    if a is None or b in (None, 0) or pd.isna(a) or pd.isna(b):
        return None
    return float(a) / float(b)


def pct(a, b):
    x = safe_div(a, b)
    return None if x is None else x * 100


def cagr(current, base, years):
    if current is None or base is None or base == 0:
        return None, "ZERO_BASE"
    if years <= 0:
        return None, "INVALID_PERIOD"
    if current < 0 or base < 0:
        return None, "NEGATIVE_BASE_OR_END"
    return ((current / base) ** (1 / years) - 1) * 100, "NORMAL"


def main():
    con = sqlite3.connect(DB)
    pnl = pd.read_sql_query("SELECT * FROM profitandloss", con)
    bs = pd.read_sql_query("SELECT * FROM balancesheet", con)
    cf = pd.read_sql_query("SELECT * FROM cashflow", con)

    if pnl.empty:
        raise RuntimeError("P&L table is empty. Run src/etl/loader.py first.")

    # Use period as the natural key. Duplicate rows were already reduced by loader.
    df = pnl.merge(
        bs, on=["company_id", "period", "year"], how="outer",
        suffixes=("", "_bs")
    ).merge(
        cf, on=["company_id", "period", "year"], how="outer"
    )

    df = df.sort_values(["company_id", "year", "period"])

    rows = []
    edge_cases = []

    for company_id, g in df.groupby("company_id", sort=False):
        g = g.sort_values(["year", "period"]).reset_index(drop=True)

        for i, r in g.iterrows():
            sales = r.get("sales")
            op = r.get("operating_profit")
            pat = r.get("net_profit")
            equity = r.get("equity")
            if pd.isna(equity):
                equity = r.get("equity_capital")
                if not pd.isna(r.get("reserves")):
                    equity = (0 if pd.isna(equity) else equity) + r.get("reserves")

            assets = r.get("total_assets")
            debt = r.get("borrowings")
            cash = r.get("cash")
            cfo = r.get("cash_from_operating")
            capex = r.get("cash_from_investing")
            eps = r.get("eps")
            dividend = r.get("dividend")
            interest = r.get("interest")

            if pd.isna(capex):
                capex = None
            else:
                capex = abs(float(capex))

            fcf = None if pd.isna(cfo) or capex is None else float(cfo) - capex

            row = {
                "company_id": company_id,
                "period": r["period"],
                "year": int(r["year"]) if not pd.isna(r["year"]) else None,
                "net_profit_margin_pct": pct(pat, sales),
                "operating_profit_margin_pct": pct(op, sales),
                "return_on_equity_pct": pct(pat, equity),
                "roce_pct": pct(op, equity),
                "return_on_assets_pct": pct(pat, assets),
                "debt_to_equity": safe_div(debt, equity),
                "high_leverage_flag": int(
                    (safe_div(debt, equity) or 0) > 5
                ),
                "interest_coverage": safe_div(op, interest),
                "icr_label": (
                    "No Interest" if interest in (None, 0) or pd.isna(interest)
                    else "Weak" if (safe_div(op, interest) or 0) < 1.5
                    else "Healthy"
                ),
                "icr_warning_flag": int(
                    interest not in (None, 0) and not pd.isna(interest)
                    and (safe_div(op, interest) or 0) < 1.5
                ),
                "net_debt_cr": None if pd.isna(debt) else float(debt) - (0 if pd.isna(cash) else float(cash)),
                "asset_turnover": safe_div(sales, assets),
                "free_cash_flow_cr": fcf,
                "cfo_quality_score": pct(cfo, pat),
                "cfo_quality_label": (
                    "Strong" if (pct(cfo, pat) or 0) >= 100
                    else "Weak" if (pct(cfo, pat) or 0) < 50
                    else "Normal"
                ),
                "capex_cr": capex,
                "capex_intensity_pct": pct(capex, sales),
                "capex_intensity_label": (
                    "High" if (pct(capex, sales) or 0) >= 15
                    else "Low" if (pct(capex, sales) or 0) < 5
                    else "Normal"
                ),
                "fcf_conversion_rate_pct": pct(fcf, pat),
                "earnings_per_share": eps,
                "book_value_per_share": safe_div(equity, 1),
                "dividend_payout_ratio_pct": pct(dividend, eps),
                "total_debt_cr": debt,
                "cash_from_operations_cr": cfo,
                "composite_quality_score": 0,
                "ebit_margin_pct": pct(op, sales),
                "tax_rate_pct": pct(r.get("tax"), r.get("profit_before_tax")),
                "expense_to_sales_pct": pct(r.get("expenses"), sales),
                "cfo_margin_pct": pct(cfo, sales),
                "fcf_margin_pct": pct(fcf, sales),
                "net_debt_to_equity": safe_div(
                    None if pd.isna(debt) else float(debt) - (0 if pd.isna(cash) else float(cash)),
                    equity
                ),
                "cash_to_debt_pct": pct(cash, debt),
                "investments_to_debt_pct": pct(r.get("investments"), debt),
            }

            # Year-on-year metrics.
            if i > 0:
                prev = g.iloc[i - 1]
                row["revenue_growth_yoy_pct"] = pct(sales - prev["sales"], prev["sales"]) if not pd.isna(sales) and not pd.isna(prev["sales"]) else None
                row["pat_growth_yoy_pct"] = pct(pat - prev["net_profit"], prev["net_profit"]) if not pd.isna(pat) and not pd.isna(prev["net_profit"]) else None
                row["eps_growth_yoy_pct"] = pct(eps - prev["eps"], prev["eps"]) if not pd.isna(eps) and not pd.isna(prev["eps"]) else None
                row["operating_profit_growth_yoy_pct"] = pct(op - prev["operating_profit"], prev["operating_profit"]) if not pd.isna(op) and not pd.isna(prev["operating_profit"]) else None
            else:
                row["revenue_growth_yoy_pct"] = None
                row["pat_growth_yoy_pct"] = None
                row["eps_growth_yoy_pct"] = None
                row["operating_profit_growth_yoy_pct"] = None

            # CAGR calculations use prior observations by year.
            for metric, prefix in [
                ("sales", "revenue"),
                ("net_profit", "pat"),
                ("eps", "eps"),
            ]:
                for years in [3, 5, 10]:
                    target = f"{prefix}_cagr_{years}yr"
                    flag = f"{target}_flag"
                    base = g.iloc[i - years] if i >= years else None
                    if base is None:
                        row[target], row[flag] = None, "INSUFFICIENT_HISTORY"
                    else:
                        value, status = cagr(
                            r[metric], base[metric], years
                        )
                        row[target], row[flag] = value, status
                        if status != "NORMAL":
                            edge_cases.append(
                                f"{company_id},{r['period']},{target},{status}"
                            )

            score_parts = [
                row["net_profit_margin_pct"],
                row["return_on_equity_pct"],
                row["roce_pct"],
            ]
            valid = [x for x in score_parts if x is not None]
            row["composite_quality_score"] = (
                sum(valid) / len(valid) if valid else 0
            )

            rows.append(row)

    ratio_df = pd.DataFrame(rows)

    columns = [
        "company_id","period","year",
        "net_profit_margin_pct","operating_profit_margin_pct",
        "return_on_equity_pct","roce_pct","return_on_assets_pct",
        "debt_to_equity","high_leverage_flag","interest_coverage",
        "icr_label","icr_warning_flag","net_debt_cr","asset_turnover",
        "free_cash_flow_cr","cfo_quality_score","cfo_quality_label",
        "capex_cr","capex_intensity_pct","capex_intensity_label",
        "fcf_conversion_rate_pct","earnings_per_share",
        "book_value_per_share","dividend_payout_ratio_pct",
        "total_debt_cr","cash_from_operations_cr",
        "revenue_cagr_3yr","revenue_cagr_3yr_flag",
        "revenue_cagr_5yr","revenue_cagr_5yr_flag",
        "revenue_cagr_10yr","revenue_cagr_10yr_flag",
        "pat_cagr_3yr","pat_cagr_3yr_flag",
        "pat_cagr_5yr","pat_cagr_5yr_flag",
        "pat_cagr_10yr","pat_cagr_10yr_flag",
        "eps_cagr_3yr","eps_cagr_3yr_flag",
        "eps_cagr_5yr","eps_cagr_5yr_flag",
        "eps_cagr_10yr","eps_cagr_10yr_flag",
        "composite_quality_score",
        "ebit_margin_pct","tax_rate_pct","expense_to_sales_pct",
        "cfo_margin_pct","fcf_margin_pct","net_debt_to_equity",
        "cash_to_debt_pct","investments_to_debt_pct",
        "revenue_growth_yoy_pct","pat_growth_yoy_pct",
        "eps_growth_yoy_pct","operating_profit_growth_yoy_pct",
    ]
    for c in columns:
        if c not in ratio_df:
            ratio_df[c] = None
    ratio_df = ratio_df[columns]

    con.execute("DELETE FROM financial_ratios")
    rows_sql = ratio_df.where(pd.notna(ratio_df), None).itertuples(index=False, name=None)
    placeholders = ",".join(["?"] * len(columns))
    con.executemany(
        f"INSERT OR REPLACE INTO financial_ratios ({','.join(columns)}) VALUES ({placeholders})",
        rows_sql
    )
    con.commit()

    # Capital allocation output.
    cap = ratio_df[[
        "company_id","period","year","free_cash_flow_cr",
        "capex_cr","capex_intensity_pct","fcf_conversion_rate_pct"
    ]].copy()
    cap["capital_allocation_pattern"] = cap.apply(
        lambda x: (
            "FCF Positive" if pd.notna(x["free_cash_flow_cr"]) and x["free_cash_flow_cr"] > 0
            else "FCF Negative"
        ),
        axis=1
    )
    cap.to_csv(OUTPUT / "capital_allocation.csv", index=False)

    (OUTPUT / "ratio_edge_cases.log").write_text(
        "\n".join(edge_cases) if edge_cases else "No ratio edge cases found.\n"
    )

    con.close()
    print(f"Financial ratio rows created: {len(ratio_df)}")


if __name__ == "__main__":
    main()
