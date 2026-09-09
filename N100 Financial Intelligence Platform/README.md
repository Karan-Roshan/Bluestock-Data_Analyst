# SPRINT 1 — DATA FOUNDATION

Easy-to-read Python/SQLite implementation for the Sprint 1 specification.

## Important specification note

The prompt says "10 tables" but explicitly lists **11 table names**:
companies, profitandloss, balancesheet, cashflow, analysis, documents, prosandcons,
sectors, stock_prices, financial_ratios, peer_groups.

This project implements all 11 named tables so no requested table is silently omitted.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## Put source files here

Place the 12 Excel files in:

`data/raw/`

The loader does not require exact filenames. It identifies files from their contents/filename keywords.

Expected broad groups:
- 7 core Excel files
- 5 supplementary Excel files

If your workbook column names differ, edit `src/etl/normaliser.py` aliases.

## Main commands

```bash
make load
make test
make validate
make report
make clean
```

The `load` command:
1. Creates `nifty100.db`
2. Creates the schema
3. Loads Excel files
4. Runs validation
5. Writes `output/load_audit.csv`
6. Writes `output/validation_failures.csv`

## Exit checks

```sql
SELECT COUNT(*) FROM companies;
PRAGMA foreign_key_check;
```

Target company count from the specification: 92.

The loader does NOT invent missing data to force a target count. If the source files do not contain 92 companies, the audit reports the actual count.

## DQ rules

DQ-01 PK uniqueness
DQ-02 (company_id, year) uniqueness
DQ-03 FK integrity
DQ-04 Balance sheet balance < 1%
DQ-05 OPM cross-check
DQ-06 Positive sales
DQ-07 Net cash check
DQ-08 Tax rate sanity
DQ-09 Dividend cap
DQ-10 URL validity
DQ-11 EPS sign check
DQ-12 BSE balance/check
DQ-13 Year coverage
DQ-14 Duplicate source rows
DQ-15 Required company fields
DQ-16 Financial ratio sanity

CRITICAL rules are marked in `src/etl/validator.py`.
