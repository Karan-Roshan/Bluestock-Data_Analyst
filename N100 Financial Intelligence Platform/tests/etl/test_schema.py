import sqlite3
from pathlib import Path


def test_schema_has_required_tables(tmp_path):
    db = tmp_path / "test.db"
    con = sqlite3.connect(db)
    con.execute("PRAGMA foreign_keys = ON")
    sql = Path("db/schema.sql").read_text()
    con.executescript(sql)

    expected = {
        "companies", "profitandloss", "balancesheet", "cashflow",
        "analysis", "documents", "prosandcons", "sectors",
        "stock_prices", "financial_ratios", "peer_groups"
    }

    actual = {
        row[0] for row in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }

    assert expected.issubset(actual)


def test_foreign_keys_are_on(tmp_path):
    db = tmp_path / "fk.db"
    con = sqlite3.connect(db)
    con.execute("PRAGMA foreign_keys = ON")
    assert con.execute("PRAGMA foreign_keys").fetchone()[0] == 1
