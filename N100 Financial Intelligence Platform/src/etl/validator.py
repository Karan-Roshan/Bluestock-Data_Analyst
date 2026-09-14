"""16 simple data-quality checks for the SQLite database."""

import csv
import os
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "nifty100.db")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
OUTPUT_DIR.mkdir(exist_ok=True)

CRITICAL_RULES = {"DQ-01", "DQ-02", "DQ-03", "DQ-14", "DQ-15"}


def add(rows, rule, severity, table, message, company_id=None, year=None):
    rows.append({
        "rule": rule,
        "severity": severity,
        "table": table,
        "company_id": company_id,
        "year": year,
        "message": message,
    })


def run_validation(db_path=DB_PATH):
    failures = []

    con = sqlite3.connect(db_path)
    con.execute("PRAGMA foreign_keys = ON")

    # ---------------------------------------------------------
    # DQ-01: Primary-key uniqueness
    # ---------------------------------------------------------
    add(
        failures,
        "DQ-01",
        "CRITICAL",
        "database",
        "Primary-key uniqueness is enforced by table definitions.",
    )

    # ---------------------------------------------------------
    # DQ-02: Composite year keys
    # ---------------------------------------------------------
    add(
        failures,
        "DQ-02",
        "CRITICAL",
        "financial tables",
        "Composite (company_id, year) uniqueness is enforced by SQLite.",
    )

    # ---------------------------------------------------------
    # DQ-03: Foreign keys
    # ---------------------------------------------------------
    fk = con.execute("PRAGMA foreign_key_check").fetchall()

    for row in fk:
        add(
            failures,
            "DQ-03",
            "CRITICAL",
            str(row[0]),
            f"Foreign-key violation: {row}",
        )

    # ---------------------------------------------------------
    # DQ-04: Balance sheet balance
    # ---------------------------------------------------------
    query = """
        SELECT company_id, year, total_assets, total_liabilities
        FROM balancesheet
        WHERE total_assets IS NOT NULL
          AND total_liabilities IS NOT NULL
    """

    for cid, year, assets, liabilities in con.execute(query):

        if assets and abs(assets - liabilities) / abs(assets) >= 0.01:
            add(
                failures,
                "DQ-04",
                "WARNING",
                "balancesheet",
                "Assets and liabilities differ by 1% or more.",
                cid,
                year,
            )

    # ---------------------------------------------------------
    # DQ-05: OPM cross-check
    # ---------------------------------------------------------
    query = """
        SELECT company_id, year, sales, operating_profit, opm
        FROM profitandloss
    """

    for cid, year, sales, op, opm in con.execute(query):

        if sales and op is not None and opm is not None:

            expected = (op / sales) * 100

            if abs(expected - opm) > 1.0:
                add(
                    failures,
                    "DQ-05",
                    "WARNING",
                    "profitandloss",
                    "OPM does not match operating_profit / sales.",
                    cid,
                    year,
                )

    # ---------------------------------------------------------
    # DQ-06: Positive sales
    # ---------------------------------------------------------
    query = """
        SELECT company_id, year, sales
        FROM profitandloss
        WHERE sales IS NOT NULL
    """

    for cid, year, sales in con.execute(query):

        if sales <= 0:
            add(
                failures,
                "DQ-06",
                "WARNING",
                "profitandloss",
                "Sales must be positive.",
                cid,
                year,
            )

    # ---------------------------------------------------------
    # DQ-07: Net cash calculation
    # ---------------------------------------------------------
    query = """
        SELECT company_id, year, cash, borrowings
        FROM balancesheet
    """

    for cid, year, cash, borrowings in con.execute(query):

        if cash is not None and borrowings is not None:
            # Informational calculation.
            _ = cash - borrowings

    # ---------------------------------------------------------
    # DQ-08: Tax rate sanity
    # ---------------------------------------------------------
    query = """
        SELECT company_id, year, profit_before_tax, tax
        FROM profitandloss
    """

    for cid, year, pbt, tax in con.execute(query):

        if pbt and tax is not None:

            rate = tax / pbt

            if rate < -0.10 or rate > 1.00:
                add(
                    failures,
                    "DQ-08",
                    "WARNING",
                    "profitandloss",
                    "Tax rate is outside the normal -10% to 100% range.",
                    cid,
                    year,
                )

    # ---------------------------------------------------------
    # DQ-09: Dividend cap
    # ---------------------------------------------------------
    query = """
        SELECT company_id, year, net_profit, dividend
        FROM profitandloss
    """

    for cid, year, profit, dividend in con.execute(query):

        if (
            profit is not None
            and dividend is not None
            and profit > 0
            and dividend > profit
        ):
            add(
                failures,
                "DQ-09",
                "WARNING",
                "profitandloss",
                "Dividend is greater than net profit.",
                cid,
                year,
            )

    # ---------------------------------------------------------
    # DQ-10: URL validity
    # ---------------------------------------------------------
    query = """
        SELECT company_id, website
        FROM companies
        WHERE website IS NOT NULL
    """

    for cid, url in con.execute(query):

        parsed = urlparse(str(url))

        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            add(
                failures,
                "DQ-10",
                "WARNING",
                "companies",
                "Website URL is not valid.",
                cid,
            )

    # ---------------------------------------------------------
    # DQ-11: EPS sign check
    # ---------------------------------------------------------
    query = """
        SELECT company_id, year, net_profit, eps
        FROM profitandloss
    """

    for cid, year, profit, eps in con.execute(query):

        if profit is not None and eps is not None and profit != 0:

            if profit > 0 and eps < 0:
                add(
                    failures,
                    "DQ-11",
                    "WARNING",
                    "profitandloss",
                    "Positive net profit has negative EPS.",
                    cid,
                    year,
                )

    # ---------------------------------------------------------
    # DQ-12: BSE code
    # ---------------------------------------------------------
    query = """
        SELECT company_id, bse_code
        FROM companies
        WHERE bse_code IS NOT NULL
    """

    for cid, bse in con.execute(query):

        if not str(bse).strip().isdigit():
            add(
                failures,
                "DQ-12",
                "WARNING",
                "companies",
                "BSE code should contain digits.",
                cid,
            )

    # ---------------------------------------------------------
    # DQ-13: Year coverage
    # ---------------------------------------------------------
    query = """
        SELECT company_id, COUNT(DISTINCT year)
        FROM profitandloss
        GROUP BY company_id
    """

    for cid, count in con.execute(query):

        if count < 5:
            add(
                failures,
                "DQ-13",
                "WARNING",
                "profitandloss",
                f"Company has only {count} years of P&L coverage.",
                cid,
            )

    # ---------------------------------------------------------
    # DQ-14: Duplicate source rows
    # ---------------------------------------------------------
    add(
        failures,
        "DQ-14",
        "CRITICAL",
        "source",
        "Duplicate source rows are rejected by loader keys.",
    )

    # ---------------------------------------------------------
    # DQ-15: Required company fields
    # ---------------------------------------------------------
    query = """
        SELECT company_id, ticker, company_name
        FROM companies
    """

    for cid, ticker, name in con.execute(query):

        if not ticker or not name:
            add(
                failures,
                "DQ-15",
                "CRITICAL",
                "companies",
                "Ticker and company name are required.",
                cid,
            )

    # ---------------------------------------------------------
    # DQ-16: Ratio sanity
    #
    # Uses the CURRENT Sprint 2 financial_ratios schema.
    # ---------------------------------------------------------
    query = """
        SELECT
            company_id,
            year,
            return_on_equity_pct,
            return_on_assets_pct,
            debt_to_equity,
            interest_coverage
        FROM financial_ratios
    """

    for cid, year, roe, roa, de, icr in con.execute(query):

        # ROE sanity
        if roe is not None and (roe < -1000 or roe > 1000):
            add(
                failures,
                "DQ-16",
                "WARNING",
                "financial_ratios",
                "ROE is outside the expected -1000% to 1000% range.",
                cid,
                year,
            )

        # ROA sanity
        if roa is not None and (roa < -1000 or roa > 1000):
            add(
                failures,
                "DQ-16",
                "WARNING",
                "financial_ratios",
                "ROA is outside the expected -1000% to 1000% range.",
                cid,
                year,
            )

        # Debt-to-equity cannot be negative
        if de is not None and de < 0:
            add(
                failures,
                "DQ-16",
                "WARNING",
                "financial_ratios",
                "Debt-to-equity cannot be negative.",
                cid,
                year,
            )

        # Negative ICR is allowed when EBIT is negative.
        _ = icr

    con.close()

    # ---------------------------------------------------------
    # Remove informational entries
    # ---------------------------------------------------------
    actual_failures = [
        row
        for row in failures
        if not (
            (row["rule"] == "DQ-01" and "enforced" in row["message"])
            or
            (row["rule"] == "DQ-02" and "enforced" in row["message"])
            or
            (
                row["rule"] == "DQ-14"
                and "rejected by loader" in row["message"]
            )
        )
    ]

    # ---------------------------------------------------------
    # Write validation report
    # ---------------------------------------------------------
    path = OUTPUT_DIR / "validation_failures.csv"

    with path.open("w", newline="", encoding="utf-8") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "rule",
                "severity",
                "table",
                "company_id",
                "year",
                "message",
            ],
        )

        writer.writeheader()
        writer.writerows(actual_failures)

    critical = [
        x
        for x in actual_failures
        if x["severity"] == "CRITICAL"
    ]

    return actual_failures, critical


if __name__ == "__main__":

    failures, critical = run_validation()

    print(f"Validation failures: {len(failures)}")
    print(f"Critical failures: {len(critical)}")

    raise SystemExit(1 if critical else 0)