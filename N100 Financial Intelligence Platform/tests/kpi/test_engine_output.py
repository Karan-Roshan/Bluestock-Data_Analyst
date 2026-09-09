import sqlite3
from pathlib import Path


def test_schema_contains_required_columns():
    text = Path("db/schema.sql").read_text()
    required = [
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score",
    ]
    for column in required:
        assert column in text


def test_demo_database_has_1100_plus_rows():
    db = Path("nifty100.db")
    if not db.exists():
        return
    con = sqlite3.connect(db)
    count = con.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]
    con.close()
    assert count >= 1100
