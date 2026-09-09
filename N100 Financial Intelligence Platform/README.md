# SPRINT 2 — FINANCIAL RATIO ENGINE

A simple, readable implementation of Sprint 2.

This project is designed to run independently and also uses the same general
SQLite/Excel structure as Sprint 1.

## What is included

- 50+ KPI calculations and derived metrics
- Profitability ratios
- Leverage and efficiency ratios
- CAGR engine with all six edge cases
- Cash-flow KPIs
- Capital allocation 8-pattern classifier
- Financial ratios SQLite table
- Bank/Financials D/E carve-out
- ROE/ROCE source cross-check
- `output/capital_allocation.csv`
- `output/ratio_edge_cases.log`
- 20+ KPI tests
- Screener preview
- Easy sample data for 92 companies and 12 years

## Important

The included data is synthetic/demo data because no real source Excel files
were supplied. It is structured to exercise the engine and satisfy the
Sprint 2 row-count shape (92 companies x 12 years = 1,104 company-years).

For production use, replace the sample Excel files in `data/raw/` with your
real source files.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 src/analytics/run_engine.py
python3 -m pytest -q
```

Or:

```bash
make setup-test
make ratios
make test
make screener
```

## Expected

- `financial_ratios` >= 1,100 rows
- 20+ tests pass
- capital allocation CSV is generated
- edge-case log is generated
