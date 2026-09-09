"""Simple derived-ratio builder."""

import sqlite3
from pathlib import Path

DB_PATH = "nifty100.db"


def build_ratios(db_path=DB_PATH):
    con = sqlite3.connect(db_path)
    rows = con.execute("""
        SELECT company_id, year, net_profit, equity, total_assets,
               borrowings, reserves
        FROM balancesheet
        JOIN profitandloss USING (company_id, year)
    """).fetchall()

    for cid, year, profit, equity, assets, debt, reserves in rows:
        roe = profit / equity * 100 if equity else None
        roa = profit / assets * 100 if assets else None
        de = debt / (equity + reserves) if (equity or reserves) else None

        con.execute("""
            INSERT OR REPLACE INTO financial_ratios
            (company_id, year, roe, roa, debt_equity)
            VALUES (?, ?, ?, ?, ?)
        """, (cid, year, roe, roa, de))

    con.commit()
    con.close()


if __name__ == "__main__":
    build_ratios()
    print("Financial ratios updated.")
