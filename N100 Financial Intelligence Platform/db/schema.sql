PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sectors (
    sector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS companies (
    company_id TEXT PRIMARY KEY,
    ticker TEXT NOT NULL UNIQUE,
    company_name TEXT NOT NULL,
    bse_code TEXT,
    nse_code TEXT,
    sector_id INTEGER,
    broad_sector TEXT,
    website TEXT,
    FOREIGN KEY (sector_id) REFERENCES sectors(sector_id)
);

CREATE TABLE IF NOT EXISTS profitandloss (
    company_id TEXT NOT NULL,
    period TEXT NOT NULL,
    year INTEGER,
    sales REAL,
    expenses REAL,
    operating_profit REAL,
    opm REAL,
    interest REAL,
    other_income REAL,
    depreciation REAL,
    profit_before_tax REAL,
    tax REAL,
    net_profit REAL,
    eps REAL,
    dividend REAL,
    PRIMARY KEY (company_id, period),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS balancesheet (
    company_id TEXT NOT NULL,
    period TEXT NOT NULL,
    year INTEGER,
    equity REAL,
    equity_capital REAL,
    reserves REAL,
    borrowings REAL,
    other_liabilities REAL,
    total_liabilities REAL,
    fixed_assets REAL,
    investments REAL,
    other_assets REAL,
    cash REAL,
    total_assets REAL,
    PRIMARY KEY (company_id, period),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS cashflow (
    company_id TEXT NOT NULL,
    period TEXT NOT NULL,
    year INTEGER,
    cash_from_operating REAL,
    cash_from_investing REAL,
    cash_from_financing REAL,
    net_cash_flow REAL,
    PRIMARY KEY (company_id, period),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS analysis (
    company_id TEXT NOT NULL,
    period TEXT,
    analysis_text TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS documents (
    document_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    period TEXT,
    document_type TEXT,
    url TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS prosandcons (
    company_id TEXT NOT NULL,
    item_type TEXT NOT NULL,
    item_text TEXT NOT NULL,
    PRIMARY KEY (company_id, item_type, item_text),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS stock_prices (
    company_id TEXT NOT NULL,
    price_date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    PRIMARY KEY (company_id, price_date),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS peer_groups (
    peer_group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT,
    sector_name TEXT,
    group_name TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS financial_ratios (
    company_id TEXT NOT NULL,
    period TEXT NOT NULL,
    year INTEGER,

    net_profit_margin_pct REAL,
    operating_profit_margin_pct REAL,
    return_on_equity_pct REAL,
    roce_pct REAL,
    return_on_assets_pct REAL,

    debt_to_equity REAL,
    high_leverage_flag INTEGER DEFAULT 0,
    interest_coverage REAL,
    icr_label TEXT,
    icr_warning_flag INTEGER DEFAULT 0,
    net_debt_cr REAL,
    asset_turnover REAL,

    free_cash_flow_cr REAL,
    cfo_quality_score REAL,
    cfo_quality_label TEXT,
    capex_cr REAL,
    capex_intensity_pct REAL,
    capex_intensity_label TEXT,
    fcf_conversion_rate_pct REAL,

    earnings_per_share REAL,
    book_value_per_share REAL,
    dividend_payout_ratio_pct REAL,
    total_debt_cr REAL,
    cash_from_operations_cr REAL,

    revenue_cagr_3yr REAL,
    revenue_cagr_3yr_flag TEXT,
    revenue_cagr_5yr REAL,
    revenue_cagr_5yr_flag TEXT,
    revenue_cagr_10yr REAL,
    revenue_cagr_10yr_flag TEXT,

    pat_cagr_3yr REAL,
    pat_cagr_3yr_flag TEXT,
    pat_cagr_5yr REAL,
    pat_cagr_5yr_flag TEXT,
    pat_cagr_10yr REAL,
    pat_cagr_10yr_flag TEXT,

    eps_cagr_3yr REAL,
    eps_cagr_3yr_flag TEXT,
    eps_cagr_5yr REAL,
    eps_cagr_5yr_flag TEXT,
    eps_cagr_10yr REAL,
    eps_cagr_10yr_flag TEXT,

    composite_quality_score REAL,

    ebit_margin_pct REAL,
    tax_rate_pct REAL,
    expense_to_sales_pct REAL,
    cfo_margin_pct REAL,
    fcf_margin_pct REAL,
    net_debt_to_equity REAL,
    cash_to_debt_pct REAL,
    investments_to_debt_pct REAL,
    revenue_growth_yoy_pct REAL,
    pat_growth_yoy_pct REAL,
    eps_growth_yoy_pct REAL,
    operating_profit_growth_yoy_pct REAL,

    PRIMARY KEY (company_id, period),
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE TABLE IF NOT EXISTS market_cap (
    company_id TEXT NOT NULL,
    period TEXT,
    market_cap REAL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);
