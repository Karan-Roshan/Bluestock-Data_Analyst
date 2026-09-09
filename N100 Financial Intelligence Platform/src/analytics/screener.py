"""Simple Sprint 2 screener: latest year, ROE > 15%, D/E < 1."""
import sqlite3

DB = "nifty100.db"
con = sqlite3.connect(DB)
latest = con.execute("SELECT MAX(year) FROM financial_ratios").fetchone()[0]
rows = con.execute("""
    SELECT company_id, year, return_on_equity_pct, debt_to_equity
    FROM financial_ratios
    WHERE year = ?
      AND return_on_equity_pct > 15
      AND debt_to_equity < 1
    ORDER BY return_on_equity_pct DESC
""", (latest,)).fetchall()

print(f"Screener: latest year={latest}, ROE > 15% and D/E < 1")
print("Company count:", len(rows))
for row in rows:
    print(row)

con.close()
