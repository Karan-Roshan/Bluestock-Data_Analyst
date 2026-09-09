PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL UNIQUE,
    company_name TEXT NOT NULL,
    bse_code TEXT,
    nse_code TEXT,
    sector_id INTEGER,
    website TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sector_id) REFERENCES sectors(sector_id)
);

CREATE TABLE IF NOT EXISTS sectors (
    sector_id INTEGER PRIMARY KEY,
    sector_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS profitandloss (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    sales REAL,
    expenses REAL,
    operating_profit REAL,
    opm REAL,
    interest REAL,
    depreciation REAL,
    profit_before_tax REAL,
    tax REAL,
    net_profit REAL,
    eps REAL,
    dividend REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS balancesheet (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    equity REAL,
    reserves REAL,
    borrowings REAL,
    other_liabilities REAL,
    total_liabilities REAL,
    fixed_assets REAL,
    investments REAL,
    other_assets REAL,
    cash REAL,
    total_assets REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS cashflow (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    cash_from_operating REAL,
    cash_from_investing REAL,
    cash_from_financing REAL,
    net_cash_flow REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS analysis (
    company_id INTEGER NOT NULL,
    year INTEGER,
    summary TEXT,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS documents (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    year INTEGER,
    document_type TEXT,
    url TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS prosandcons (
    company_id INTEGER NOT NULL,
    item_type TEXT NOT NULL,
    item_text TEXT NOT NULL,
    PRIMARY KEY (company_id, item_type, item_text),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS stock_prices (
    company_id INTEGER NOT NULL,
    price_date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    PRIMARY KEY (company_id, price_date),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS financial_ratios (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    pe REAL,
    pb REAL,
    roe REAL,
    roa REAL,
    debt_equity REAL,
    current_ratio REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS peer_groups (
    peer_group_id INTEGER PRIMARY KEY,
    sector_id INTEGER,
    group_name TEXT NOT NULL,
    FOREIGN KEY (sector_id) REFERENCES sectors(sector_id)
);
