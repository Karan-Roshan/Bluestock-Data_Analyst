import pandas as pd

df = pd.read_csv("../data/raw/scheme_performance.csv")

# View the first few rows
print("\n-- First five rows --")
print(df.head(5))

# Check the dataset information
print("\n-- Dataset information --")
print(df.info())

# Check null value
print("\n-- Check any null value --")
print(df.isnull().sum())

# Convert Return Columns to Numeric
text_cols = [
    "scheme_name",
    "fund_house",
    "category",
    "plan",
    "risk_grade"
]

for col in df.columns:
    if col not in text_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

print("\n-- Convert Return Columns to Numeric --")
print(df.dtypes)

# Flag Invalid / Non-Numeric Values
numeric_cols = [
    "return_1yr_pct",
    "return_3yr_pct",
    "return_5yr_pct",
    "benchmark_3yr_pct",
    "alpha",
    "beta",
    "sharpe_ratio",
    "sortino_ratio",
    "std_dev_ann_pct",
    "max_drawdown_pct",
    "aum_crore",
    "expense_ratio_pct",
    "morningstar_rating"
]

anomalies = df[df[numeric_cols].isnull().any(axis=1)]

print("\nNumber of anomaly rows:", len(anomalies))

print("\n-- Anomalies --")
print(anomalies)

# Check Expense Ratio Range (0.1%–2.5%)
invalid_expense = df[
    (df["expense_ratio_pct"] < 0.1) |
    (df["expense_ratio_pct"] > 2.5)
]

print("\n-- Invalid Expense Ratio Rows --")
print(invalid_expense)

df = df[
    (df["expense_ratio_pct"] >= 0.1) &
    (df["expense_ratio_pct"] <= 2.5)
].reset_index(drop=True)

# Save the Cleaned File
df.to_csv("../data/raw/scheme_performance.csv", index=False)


print("\nScheme Performance cleaned successfully!")