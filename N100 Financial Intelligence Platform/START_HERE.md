# START HERE

This ZIP is ready to put inside your project.

## 1. Open terminal in this folder

```bash
cd sprint1_data_foundation
```

## 2. Create environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install packages

```bash
python3 -m pip install -r requirements.txt
```

## 4. Run tests

```bash
python3 -m pytest -q
```

## 5. Load the sample Excel files

```bash
python3 src/etl/loader.py
```

## 6. Check the database

```bash
sqlite3 nifty100.db
```

Then:

```sql
SELECT * FROM companies;
PRAGMA foreign_key_check;
.quit
```

### Note

The Excel files included here are **small sample files** because no real source files were provided.
They are intended to make the project easy to run and understand. They do not represent the full
92-company Nifty 100 dataset.

The original Sprint target of 92 companies and the approximate row counts can only be achieved from
the real source data.
