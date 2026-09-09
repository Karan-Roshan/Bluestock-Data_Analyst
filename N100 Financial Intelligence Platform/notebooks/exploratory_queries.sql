-- 01 Company count
SELECT COUNT(*) AS companies FROM companies;

-- 02 P&L row count
SELECT COUNT(*) AS pnl_rows FROM profitandloss;

-- 03 Balance sheet row count
SELECT COUNT(*) AS bs_rows FROM balancesheet;

-- 04 Cash flow row count
SELECT COUNT(*) AS cashflow_rows FROM cashflow;

-- 05 Stock-price row count
SELECT COUNT(*) AS price_rows FROM stock_prices;

-- 06 Companies with fewer than five P&L years
SELECT company_id, COUNT(*) AS years
FROM profitandloss
GROUP BY company_id
HAVING COUNT(*) < 5;

-- 07 Latest profit by company
SELECT company_id, year, net_profit
FROM profitandloss
WHERE (company_id, year) IN (
    SELECT company_id, MAX(year)
    FROM profitandloss
    GROUP BY company_id
);

-- 08 Balance-sheet difference
SELECT company_id, year,
       total_assets,
       total_liabilities,
       total_assets - total_liabilities AS difference
FROM balancesheet
WHERE total_assets IS NOT NULL
  AND total_liabilities IS NOT NULL;

-- 09 Top companies by latest net profit
SELECT company_id, year, net_profit
FROM profitandloss
WHERE year = (SELECT MAX(year) FROM profitandloss)
ORDER BY net_profit DESC
LIMIT 20;

-- 10 Foreign-key check
PRAGMA foreign_key_check;
