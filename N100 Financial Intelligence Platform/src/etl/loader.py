"""Excel -> SQLite loader.

The code is intentionally straightforward. It reads every .xlsx/.xlsm file,
tries to identify its table from filename/columns, normalises values, and
loads the database in FK-safe order.
"""

import os
import re
import sqlite3
import csv
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from normaliser import (
    clean_column_name,
    normalize_number,
    normalize_ticker,
    normalize_year,
)

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "nifty100.db")
RAW_DATA_DIR = Path(os.getenv("RAW_DATA_DIR", "data/raw"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
SCHEMA_PATH = Path(os.getenv("SCHEMA_PATH", "db/schema.sql"))

OUTPUT_DIR.mkdir(exist_ok=True)


def read_excel_file(path):
    """Read all sheets and combine them."""
    sheets = pd.read_excel(path, sheet_name=None)
    frames = []
    for sheet_name, frame in sheets.items():
        if frame is None or frame.empty:
            continue
        frame = frame.copy()
        frame["__source_sheet"] = sheet_name
        frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def normalise_dataframe(df):
    df = df.copy()
    df.columns = [clean_column_name(c) for c in df.columns]

    for col in df.columns:
        if col in {"year", "fy", "financial_year"}:
            df[col] = df[col].map(normalize_year)
        elif "ticker" in col or col in {"symbol", "nse_code"}:
            df[col] = df[col].map(normalize_ticker)
        else:
            # Only convert obvious numeric-looking values.
            if df[col].dtype == "object":
                sample = df[col].dropna().astype(str).head(20)
                if not sample.empty:
                    numeric = sample.map(normalize_number)
                    if numeric.notna().sum() >= max(1, len(sample) // 2):
                        df[col] = df[col].map(normalize_number)
    return df


def identify_table(path, df):
    name = path.stem.lower()
    columns = set(df.columns)

    checks = [
        (["profit", "pnl", "pl"], "profitandloss"),
        (["balance", "bs"], "balancesheet"),
        (["cashflow", "cash_flow", "cash"], "cashflow"),
        (["price", "stock"], "stock_prices"),
        (["ratio"], "financial_ratios"),
        (["pros", "cons"], "prosandcons"),
        (["document", "annual_report"], "documents"),
        (["peer"], "peer_groups"),
        (["sector"], "sectors"),
        (["analysis"], "analysis"),
        (["compan", "company", "nifty"], "companies"),
    ]

    for words, table in checks:
        if any(word in name for word in words):
            return table

    if {"ticker", "sales"} & columns:
        return "profitandloss"
    if {"ticker", "total_assets"} & columns:
        return "balancesheet"
    if {"ticker", "close"} & columns:
        return "stock_prices"
    return None


ALIASES = {
    "ticker": ["ticker", "symbol", "nse_ticker", "nse_code"],
    "company_name": ["company_name", "company", "name"],
    "bse_code": ["bse_code", "bse"],
    "nse_code": ["nse_code", "nse"],
    "sector_id": ["sector_id"],
    "sector_name": ["sector_name", "sector"],
    "year": ["year", "fy", "financial_year"],
    "sales": ["sales", "revenue", "net_sales"],
    "expenses": ["expenses", "total_expenses"],
    "operating_profit": ["operating_profit", "op_profit"],
    "opm": ["opm", "operating_profit_margin"],
    "interest": ["interest"],
    "depreciation": ["depreciation"],
    "profit_before_tax": ["profit_before_tax", "pbt"],
    "tax": ["tax", "tax_expense"],
    "net_profit": ["net_profit", "profit_after_tax", "pat"],
    "eps": ["eps", "earnings_per_share"],
    "dividend": ["dividend", "dividend_per_share"],
    "equity": ["equity", "shareholders_equity"],
    "reserves": ["reserves"],
    "borrowings": ["borrowings", "debt"],
    "other_liabilities": ["other_liabilities"],
    "total_liabilities": ["total_liabilities"],
    "fixed_assets": ["fixed_assets"],
    "investments": ["investments"],
    "other_assets": ["other_assets"],
    "cash": ["cash", "cash_and_equivalents"],
    "total_assets": ["total_assets"],
    "cash_from_operating": ["cash_from_operating", "cfo"],
    "cash_from_investing": ["cash_from_investing", "cfi"],
    "cash_from_financing": ["cash_from_financing", "cff"],
    "net_cash_flow": ["net_cash_flow"],
    "price_date": ["price_date", "date"],
    "open": ["open"],
    "high": ["high"],
    "low": ["low"],
    "close": ["close"],
    "volume": ["volume"],
    "pe": ["pe", "p_e"],
    "pb": ["pb", "p_b"],
    "roe": ["roe"],
    "roa": ["roa"],
    "debt_equity": ["debt_equity", "de_ratio"],
    "current_ratio": ["current_ratio"],
    "website": ["website", "url"],
}


def find_value(row, logical_name):
    for alias in ALIASES.get(logical_name, [logical_name]):
        if alias in row.index:
            return row[alias]
    return None


def company_id_map(con):
    return {
        ticker: cid
        for cid, ticker in con.execute("SELECT company_id, ticker FROM companies")
        if ticker
    }


def get_or_create_company(con, row):
    ticker = normalize_ticker(find_value(row, "ticker"))
    name = find_value(row, "company_name") or ticker

    if not ticker:
        return None, "missing ticker"

    existing = con.execute(
        "SELECT company_id FROM companies WHERE ticker = ?", (ticker,)
    ).fetchone()
    if existing:
        return existing[0], None

    next_id = con.execute(
        "SELECT COALESCE(MAX(company_id), 0) + 1 FROM companies"
    ).fetchone()[0]

    con.execute(
        """INSERT INTO companies
        (company_id, ticker, company_name, bse_code, nse_code, website)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (
            next_id,
            ticker,
            str(name),
            find_value(row, "bse_code"),
            find_value(row, "nse_code") or ticker,
            find_value(row, "website"),
        ),
    )
    return next_id, None


def load_table(con, table, df, audit):
    df = normalise_dataframe(df)

    for _, row in df.iterrows():
        try:
            cid, error = get_or_create_company(con, row)
            if error:
                audit.append([table, "REJECTED", "CRITICAL", error])
                continue

            year = normalize_year(find_value(row, "year"))

            if table == "companies":
                continue

            if table == "sectors":
                sector_name = find_value(row, "sector_name")
                if sector_name:
                    con.execute(
                        "INSERT OR IGNORE INTO sectors(sector_name) VALUES (?)",
                        (str(sector_name),),
                    )
                continue

            if table == "profitandloss":
                if year is None:
                    audit.append([table, "REJECTED", "CRITICAL", "missing year"])
                    continue
                values = [normalize_number(find_value(row, x)) for x in [
                    "sales", "expenses", "operating_profit", "opm", "interest",
                    "depreciation", "profit_before_tax", "tax", "net_profit",
                    "eps", "dividend"
                ]]
                con.execute(
                    """INSERT OR REPLACE INTO profitandloss
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (cid, year, *values),
                )

            elif table == "balancesheet":
                if year is None:
                    audit.append([table, "REJECTED", "CRITICAL", "missing year"])
                    continue
                values = [normalize_number(find_value(row, x)) for x in [
                    "equity", "reserves", "borrowings", "other_liabilities",
                    "total_liabilities", "fixed_assets", "investments",
                    "other_assets", "cash", "total_assets"
                ]]
                con.execute(
                    """INSERT OR REPLACE INTO balancesheet
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (cid, year, *values),
                )

            elif table == "cashflow":
                if year is None:
                    audit.append([table, "REJECTED", "CRITICAL", "missing year"])
                    continue
                values = [normalize_number(find_value(row, x)) for x in [
                    "cash_from_operating", "cash_from_investing",
                    "cash_from_financing", "net_cash_flow"
                ]]
                con.execute(
                    """INSERT OR REPLACE INTO cashflow
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (cid, year, *values),
                )

            elif table == "stock_prices":
                date = find_value(row, "price_date")
                if pd.isna(date):
                    audit.append([table, "REJECTED", "WARNING", "missing date"])
                    continue
                date = pd.to_datetime(date).date().isoformat()
                values = [normalize_number(find_value(row, x))
                          for x in ["open", "high", "low", "close", "volume"]]
                con.execute(
                    """INSERT OR REPLACE INTO stock_prices
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (cid, date, *values),
                )

            elif table == "financial_ratios":
                if year is None:
                    audit.append([table, "REJECTED", "CRITICAL", "missing year"])
                    continue
                values = [normalize_number(find_value(row, x)) for x in
                          ["pe", "pb", "roe", "roa", "debt_equity", "current_ratio"]]
                con.execute(
                    """INSERT OR REPLACE INTO financial_ratios
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (cid, year, *values),
                )

            elif table == "documents":
                con.execute(
                    """INSERT INTO documents(company_id, year, document_type, url)
                    VALUES (?, ?, ?, ?)""",
                    (cid, year, find_value(row, "document_type"),
                     find_value(row, "website")),
                )

            elif table == "analysis":
                con.execute(
                    """INSERT OR REPLACE INTO analysis(company_id, year, summary)
                    VALUES (?, ?, ?)""",
                    (cid, year, str(find_value(row, "summary") or "")),
                )

            elif table == "prosandcons":
                item_type = str(find_value(row, "item_type") or "unknown")
                item_text = str(find_value(row, "item_text") or "")
                if item_text:
                    con.execute(
                        """INSERT OR IGNORE INTO prosandcons
                        VALUES (?, ?, ?)""",
                        (cid, item_type, item_text),
                    )

            audit.append([table, "LOADED", "INFO", ""])

        except Exception as exc:
            audit.append([table, "REJECTED", "CRITICAL", str(exc)])


def load_all():
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema not found: {SCHEMA_PATH}")

    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

    audit = []
    paths = sorted(RAW_DATA_DIR.glob("*.xlsx")) + sorted(RAW_DATA_DIR.glob("*.xlsm"))

    if not paths:
        print("No Excel files found in data/raw/. Add the 12 source files first.")

    for path in paths:
        try:
            df = read_excel_file(path)
            if df.empty:
                audit.append([path.name, "REJECTED", "WARNING", "empty workbook"])
                continue

            table = identify_table(path, normalise_dataframe(df))
            if table is None:
                audit.append([path.name, "REJECTED", "WARNING", "could not identify table"])
                continue

            before = len(audit)
            load_table(con, table, df, audit)
            loaded = sum(1 for x in audit[before:] if x[1] == "LOADED")
            rejected = sum(1 for x in audit[before:] if x[1] == "REJECTED")
            print(f"{path.name}: {table} -> loaded={loaded}, rejected={rejected}")

        except Exception as exc:
            audit.append([path.name, "REJECTED", "CRITICAL", str(exc)])

    con.commit()

    with (OUTPUT_DIR / "load_audit.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_or_table", "status", "severity", "message"])
        writer.writerows(audit)

    con.close()
    print(f"Database created: {DB_PATH}")
    print(f"Audit written: {OUTPUT_DIR / 'load_audit.csv'}")


if __name__ == "__main__":
    load_all()
    # Run validation after loading.
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from validator import run_validation
    failures, critical = run_validation(DB_PATH)
    print(f"Validation failures: {len(failures)}")
    print(f"CRITICAL failures: {len(critical)}")
    if critical:
        raise SystemExit(1)
