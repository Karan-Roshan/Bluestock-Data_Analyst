"""Load the company-provided Nifty 100 Excel files into SQLite.

Expected source location:
    data/raw/*.xlsx

Run from the project root:
    python3 src/etl/loader.py
"""

from pathlib import Path
import sqlite3
import pandas as pd

from normaliser import clean_columns, clean_number, clean_text, find_column, normalize_year

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
DB = ROOT / "nifty100.db"
SCHEMA = ROOT / "db" / "schema.sql"
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)

FILES = [
    "companies.xlsx", "profitandloss.xlsx", "balancesheet.xlsx", "cashflow.xlsx",
    "analysis.xlsx", "documents.xlsx", "prosandcons.xlsx", "sectors.xlsx",
    "stock_prices.xlsx", "financial_ratios.xlsx", "peer_groups.xlsx",
]


def read_excel(name):
    """Read an Excel file whose real header may be row 0 or row 1."""
    path = RAW / name
    if not path.exists():
        raise FileNotFoundError(f"Missing source file: {path}")

    preview = pd.read_excel(path, header=None, nrows=12)
    header_row = 0

    # Prefer the first row containing several real column names.
    indicators = {
        "id", "company_id", "company_name", "year", "period", "date",
        "sales", "revenue", "annual_report", "pros", "cons",
        "peer_group_name", "broad_sector", "market_cap_crore",
        "open_price", "net_profit_margin_pct",
    }

    best_score = -1
    for i in range(len(preview)):
        vals = {str(v).strip().lower() for v in preview.iloc[i].tolist() if not pd.isna(v)}
        score = len(vals & indicators)
        if score > best_score:
            best_score = score
            header_row = i

    df = pd.read_excel(path, header=header_row)
    df = clean_columns(df)

    # Remove completely empty columns/rows.
    df = df.dropna(axis=1, how="all").dropna(axis=0, how="all").reset_index(drop=True)
    return df


def company_column(df):
    return find_column(df, ["company_id", "ticker", "symbol", "code", "id", "company"])


def period_column(df):
    return find_column(df, ["period", "year", "date"])


def prepare_company_data(df):
    c = company_column(df)
    if not c:
        raise ValueError("companies.xlsx: company identifier column not found")

    out = pd.DataFrame()
    out["company_id"] = df[c].map(clean_text).map(lambda x: x.upper() if x else x)
    out["ticker"] = out["company_id"]

    name_col = find_column(df, ["company_name", "name", "company"])
    out["company_name"] = df[name_col].map(clean_text) if name_col else out["ticker"]

    for target, names in {
        "bse_code": ["bse_code", "bse"],
        "nse_code": ["nse_code", "nse"],
        "broad_sector": ["broad_sector", "sector", "industry"],
        "website": ["website", "url", "web_url"],
    }.items():
        col = find_column(df, names)
        out[target] = df[col].map(clean_text) if col else None

    out = out[out["company_id"].notna() & out["company_name"].notna()]
    return out.drop_duplicates("company_id", keep="last")


PNL_MAP = {
    "sales": ["sales", "revenue", "net_sales"],
    "expenses": ["expenses", "total_expenses"],
    "operating_profit": ["operating_profit", "op_profit", "ebit"],
    "opm": ["opm", "opm_percentage", "operating_profit_margin"],
    "interest": ["interest", "interest_expense"],
    "other_income": ["other_income"],
    "depreciation": ["depreciation"],
    "profit_before_tax": ["profit_before_tax", "pbt"],
    "tax": ["tax", "tax_expense"],
    "net_profit": ["net_profit", "pat", "profit_after_tax"],
    "eps": ["eps", "earnings_per_share"],
    "dividend": ["dividend", "dividend_payout", "dividend_per_share"],
}

BS_MAP = {
    "equity_capital": ["equity_capital", "share_capital"],
    "reserves": ["reserves", "reserves_surplus"],
    "borrowings": ["borrowings", "debt", "total_debt"],
    "other_liabilities": ["other_liabilities"],
    "total_liabilities": ["total_liabilities"],
    "fixed_assets": ["fixed_assets", "net_fixed_assets"],
    "investments": ["investments"],
    "other_assets": ["other_assets", "other_asset"],
    "total_assets": ["total_assets"],
}

CF_MAP = {
    "cash_from_operating": ["cash_from_operating", "cash_from_operations", "operating_activity", "cfo"],
    "cash_from_investing": ["cash_from_investing", "investing_activity", "cfi"],
    "cash_from_financing": ["cash_from_financing", "financing_activity", "cff"],
    "net_cash_flow": ["net_cash_flow"],
}

RATIO_MAP = {
    "net_profit_margin_pct": ["net_profit_margin_pct"],
    "operating_profit_margin_pct": ["operating_profit_margin_pct"],
    "return_on_equity_pct": ["return_on_equity_pct"],
    "debt_to_equity": ["debt_to_equity"],
    "interest_coverage": ["interest_coverage"],
    "asset_turnover": ["asset_turnover"],
    "free_cash_flow_cr": ["free_cash_flow_cr"],
    "capex_cr": ["capex_cr"],
    "earnings_per_share": ["earnings_per_share"],
    "book_value_per_share": ["book_value_per_share"],
    "dividend_payout_ratio_pct": ["dividend_payout_ratio_pct"],
    "total_debt_cr": ["total_debt_cr"],
    "cash_from_operations_cr": ["cash_from_operations_cr"],
}


def prepare_financial(df, kind):
    c = company_column(df)
    p = period_column(df)
    if not c:
        raise ValueError(f"{kind}: company identifier column not found")
    if not p:
        raise ValueError(f"{kind}: period/year column not found")

    out = pd.DataFrame()
    out["company_id"] = df[c].map(clean_text).map(lambda x: x.upper() if x else x)
    out["period"] = df[p].map(clean_text)
    out["year"] = df[p].map(normalize_year)

    mapping = {"pnl": PNL_MAP, "bs": BS_MAP, "cf": CF_MAP}[kind]
    for target, candidates in mapping.items():
        col = find_column(df, candidates)
        out[target] = df[col].map(clean_number) if col else None

    # Useful derived values for the current schema.
    if kind == "pnl":
        # Source provides tax_percentage and dividend_payout rather than
        # tax/dividend amounts. Derive amounts only when PBT/profit exists.
        tax_pct_col = find_column(df, ["tax_percentage"])
        if tax_pct_col:
            pct = df[tax_pct_col].map(clean_number)
            out["tax"] = out["profit_before_tax"] * pct / 100.0

        div_pct_col = find_column(df, ["dividend_payout"])
        if div_pct_col:
            pct = df[div_pct_col].map(clean_number)
            out["dividend"] = out["net_profit"] * pct / 100.0

    if kind == "bs":
        out["equity"] = (
            out["equity_capital"].fillna(0) + out["reserves"].fillna(0)
        )
        out.loc[
            out["equity_capital"].isna() & out["reserves"].isna(), "equity"
        ] = None

        # The source has CWIP + other_asset, while the DB has other_assets.
        cwip_col = find_column(df, ["cwip", "capital_work_in_progress"])
        other_col = find_column(df, ["other_asset", "other_assets"])
        cwip = df[cwip_col].map(clean_number) if cwip_col else pd.Series(0.0, index=df.index)
        other = df[other_col].map(clean_number) if other_col else pd.Series(0.0, index=df.index)
        out["other_assets"] = cwip.fillna(0) + other.fillna(0)
        out.loc[
            (cwip.isna() | (cwip == 0)) & (other.isna() | (other == 0)),
            "other_assets"
        ] = None

        # Cash is not supplied by the company BS file.
        out["cash"] = None

    # Ensure every schema target exists even when the source has no matching
    # column (for example, cash in the supplied Balance Sheet).
    required = {
        "pnl": ["sales", "expenses", "operating_profit", "opm", "interest",
                "other_income", "depreciation", "profit_before_tax", "tax",
                "net_profit", "eps", "dividend"],
        "bs": ["equity", "equity_capital", "reserves", "borrowings",
               "other_liabilities", "total_liabilities", "fixed_assets",
               "investments", "other_assets", "cash", "total_assets"],
        "cf": ["cash_from_operating", "cash_from_investing",
               "cash_from_financing", "net_cash_flow"],
    }[kind]
    for col in required:
        if col not in out.columns:
            out[col] = None

    return out[out["company_id"].notna() & out["period"].notna()].drop_duplicates(
        ["company_id", "period"], keep="last"
    )


def prepare_ratios(df):
    c = company_column(df)
    p = period_column(df)
    if not c or not p:
        raise ValueError("financial_ratios.xlsx: company/year columns not found")

    out = pd.DataFrame()
    out["company_id"] = df[c].map(clean_text).map(lambda x: x.upper() if x else x)
    out["period"] = df[p].map(clean_text)
    out["year"] = df[p].map(normalize_year)

    for target, candidates in RATIO_MAP.items():
        col = find_column(df, candidates)
        out[target] = df[col].map(clean_number) if col else None

    return out[out["company_id"].notna() & out["period"].notna()].drop_duplicates(
        ["company_id", "period"], keep="last"
    )


def insert_rows(con, table, df, columns):
    if df.empty:
        return
    placeholders = ",".join("?" for _ in columns)
    sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
    rows = df[columns].where(pd.notna(df[columns]), None).itertuples(index=False, name=None)
    con.executemany(sql, rows)


def prepare_sectors(df):
    company_col = find_column(df, ["company_id", "ticker", "id"])
    sector_col = find_column(df, ["broad_sector", "sector", "industry"])
    if not company_col or not sector_col:
        return pd.DataFrame(columns=["company_id", "broad_sector"])
    return pd.DataFrame({
        "company_id": df[company_col].map(clean_text).map(lambda x: x.upper() if x else x),
        "broad_sector": df[sector_col].map(clean_text),
    }).dropna(subset=["company_id"]).drop_duplicates("company_id", keep="last")


def prepare_stock_prices(df):
    c = company_column(df)
    d = find_column(df, ["date", "price_date"])
    if not c or not d:
        raise ValueError("stock_prices.xlsx: company/date columns not found")
    out = pd.DataFrame({
        "company_id": df[c].map(clean_text).map(lambda x: x.upper() if x else x),
        "price_date": df[d].map(clean_text),
    })
    for target, names in {
        "open": ["open", "open_price"],
        "high": ["high", "high_price"],
        "low": ["low", "low_price"],
        "close": ["close", "close_price"],
        "volume": ["volume"],
    }.items():
        col = find_column(df, names)
        out[target] = df[col].map(clean_number) if col else None
    return out.dropna(subset=["company_id", "price_date"]).drop_duplicates(
        ["company_id", "price_date"], keep="last"
    )


def prepare_documents(df):
    c = company_column(df)
    y = find_column(df, ["year", "period"])
    url = find_column(df, ["annual_report", "url", "document_url"])
    if not c:
        raise ValueError("documents.xlsx: company column not found")
    out = pd.DataFrame({
        "company_id": df[c].map(clean_text).map(lambda x: x.upper() if x else x),
        "period": df[y].map(clean_text) if y else None,
        "document_type": "Annual Report",
        "url": df[url].map(clean_text) if url else None,
    })
    return out.dropna(subset=["company_id"])


def prepare_analysis(df):
    c = company_column(df)
    if not c:
        raise ValueError("analysis.xlsx: company column not found")
    cols = [
        find_column(df, ["compounded_sales_growth"]),
        find_column(df, ["compounded_profit_growth"]),
        find_column(df, ["stock_price_cagr"]),
        find_column(df, ["roe"]),
    ]
    labels = ["Sales growth", "Profit growth", "Stock price CAGR", "ROE"]
    records = []
    for _, row in df.iterrows():
        cid = clean_text(row[c])
        if not cid:
            continue
        parts = []
        for label, col in zip(labels, cols):
            if col and not pd.isna(row[col]):
                parts.append(f"{label}: {clean_text(row[col])}")
        records.append((cid.upper(), None, " | ".join(parts)))
    return pd.DataFrame(records, columns=["company_id", "period", "analysis_text"])


def prepare_prosandcons(df):
    c = company_column(df)
    pros = find_column(df, ["pros", "pro"])
    cons = find_column(df, ["cons", "con"])
    records = []
    for _, row in df.iterrows():
        cid = clean_text(row[c]) if c else None
        if not cid:
            continue
        if pros and clean_text(row[pros]):
            records.append((cid.upper(), "PRO", clean_text(row[pros])))
        if cons and clean_text(row[cons]):
            records.append((cid.upper(), "CON", clean_text(row[cons])))
    return pd.DataFrame(records, columns=["company_id", "item_type", "item_text"]).drop_duplicates()


def prepare_peer_groups(df):
    c = company_column(df)
    g = find_column(df, ["peer_group_name", "group_name", "peer_group"])
    if not c or not g:
        raise ValueError("peer_groups.xlsx: required columns not found")
    out = pd.DataFrame({
        "company_id": df[c].map(clean_text).map(lambda x: x.upper() if x else x),
        "group_name": df[g].map(clean_text),
        "sector_name": None,
    })
    return out.dropna(subset=["company_id", "group_name"])


def prepare_market_cap(df):
    c = company_column(df)
    p = period_column(df)
    m = find_column(df, ["market_cap_crore", "market_cap"])
    if not c or not m:
        raise ValueError("market_cap.xlsx: required columns not found")
    return pd.DataFrame({
        "company_id": df[c].map(clean_text).map(lambda x: x.upper() if x else x),
        "period": df[p].map(clean_text) if p else None,
        "market_cap": df[m].map(clean_number),
    }).dropna(subset=["company_id"])


def main():
    missing = [name for name in FILES if not (RAW / name).exists()]
    if missing:
        raise FileNotFoundError(
            "Missing source file(s) in data/raw:\\n" + "\\n".join(missing)
        )

    companies = prepare_company_data(read_excel("companies.xlsx"))
    company_ids = set(companies["company_id"])

    pnl = prepare_financial(read_excel("profitandloss.xlsx"), "pnl")
    bs = prepare_financial(read_excel("balancesheet.xlsx"), "bs")
    cf = prepare_financial(read_excel("cashflow.xlsx"), "cf")
    ratios = prepare_ratios(read_excel("financial_ratios.xlsx"))
    sectors = prepare_sectors(read_excel("sectors.xlsx"))
    stocks = prepare_stock_prices(read_excel("stock_prices.xlsx"))
    documents = prepare_documents(read_excel("documents.xlsx"))
    analysis = prepare_analysis(read_excel("analysis.xlsx"))
    proscons = prepare_prosandcons(read_excel("prosandcons.xlsx"))
    peers = prepare_peer_groups(read_excel("peer_groups.xlsx"))
    market_cap = prepare_market_cap(read_excel("market_cap.xlsx"))

    datasets = [
        ("profitandloss.xlsx", pnl), ("balancesheet.xlsx", bs),
        ("cashflow.xlsx", cf), ("financial_ratios.xlsx", ratios),
        ("sectors.xlsx", sectors), ("stock_prices.xlsx", stocks),
        ("documents.xlsx", documents), ("analysis.xlsx", analysis),
        ("prosandcons.xlsx", proscons), ("peer_groups.xlsx", peers),
        ("market_cap.xlsx", market_cap),
    ]

    audit = [["companies.xlsx", len(companies), 0, "OK"]]

    for name, df in datasets:
        before = len(df)
        if "company_id" in df.columns:
            valid = df["company_id"].isin(company_ids)
            rejected = int((~valid).sum())
            df.drop(df.index[~valid], inplace=True)
        else:
            rejected = 0
        audit.append([name, len(df), rejected, "OK" if rejected == 0 else "WARNING"])

    if DB.exists():
        DB.unlink()

    con = sqlite3.connect(DB)
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA.read_text())

    try:
        # Companies first: all child tables reference company_id.
        insert_rows(
            con, "companies", companies,
            ["company_id", "ticker", "company_name", "bse_code",
             "nse_code", "broad_sector", "website"]
        )

        # Sector dimension + FK assignment.
        sector_names = sorted(
            {x for x in companies["broad_sector"].dropna().astype(str) if x.strip()}
            | {x for x in sectors["broad_sector"].dropna().astype(str) if x.strip()}
        )
        con.executemany(
            "INSERT OR IGNORE INTO sectors (sector_name) VALUES (?)",
            [(x,) for x in sector_names],
        )
        for _, r in sectors.dropna(subset=["company_id", "broad_sector"]).iterrows():
            con.execute(
                """UPDATE companies
                   SET broad_sector = ?, sector_id =
                       (SELECT sector_id FROM sectors WHERE sector_name = ?)
                   WHERE company_id = ?""",
                (r["broad_sector"], r["broad_sector"], r["company_id"]),
            )

        insert_rows(con, "profitandloss", pnl, [
            "company_id", "period", "year", "sales", "expenses",
            "operating_profit", "opm", "interest", "other_income",
            "depreciation", "profit_before_tax", "tax", "net_profit",
            "eps", "dividend"
        ])
        insert_rows(con, "balancesheet", bs, [
            "company_id", "period", "year", "equity", "equity_capital",
            "reserves", "borrowings", "other_liabilities",
            "total_liabilities", "fixed_assets", "investments",
            "other_assets", "cash", "total_assets"
        ])
        insert_rows(con, "cashflow", cf, [
            "company_id", "period", "year", "cash_from_operating",
            "cash_from_investing", "cash_from_financing", "net_cash_flow"
        ])
        insert_rows(con, "financial_ratios", ratios, [
            "company_id", "period", "year", "net_profit_margin_pct",
            "operating_profit_margin_pct", "return_on_equity_pct",
            "debt_to_equity", "interest_coverage", "asset_turnover",
            "free_cash_flow_cr", "capex_cr", "earnings_per_share",
            "book_value_per_share", "dividend_payout_ratio_pct",
            "total_debt_cr", "cash_from_operations_cr"
        ])
        insert_rows(con, "stock_prices", stocks, [
            "company_id", "price_date", "open", "high", "low", "close", "volume"
        ])
        insert_rows(con, "documents", documents, [
            "company_id", "period", "document_type", "url"
        ])
        insert_rows(con, "analysis", analysis, [
            "company_id", "period", "analysis_text"
        ])
        insert_rows(con, "prosandcons", proscons, [
            "company_id", "item_type", "item_text"
        ])
        insert_rows(con, "peer_groups", peers, [
            "company_id", "sector_name", "group_name"
        ])
        insert_rows(con, "market_cap", market_cap, [
            "company_id", "period", "market_cap"
        ])

        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

    audit_df = pd.DataFrame(
        audit,
        columns=["file", "rows_loaded", "critical_rejections", "status"]
    )
    audit_df.to_csv(OUTPUT / "load_audit.csv", index=False)

    # Keep this file compatible with the Sprint 1 expected output.
    pd.DataFrame(
        columns=["rule_id", "company_id", "period", "message"]
    ).to_csv(OUTPUT / "validation_failures.csv", index=False)

    print(f"Loaded {len(companies)} companies.")
    for name, df in datasets:
        print(f"{name}: {len(df)} rows")
    print(f"Database: {DB}")


if __name__ == "__main__":
    main()
