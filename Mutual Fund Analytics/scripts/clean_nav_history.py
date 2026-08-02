import pandas as pd

df = pd.read_csv("../data/raw/nav_history.csv")

# View the first few rows
print("\n-- First five rows --")
print(df.head(5))

# Check the dataset information
print("\n-- Dataset information --")
print(df.info())

# Convert Date to Datetime
df["date"] = pd.to_datetime(df["date"])

print("\n-- Check the data type --")
print(df["date"].dtype)

# Sort by AMFI Code and Date
df = df.sort_values(["amfi_code", "date"], ignore_index= True)

print(df.head)

# Forward-Fill Missing NAV Values
print("\n-- Calculate nav null value --")
print(df["nav"].isnull().sum())

# Fill missing values
df["nav"] = df.groupby("amfi_code")["nav"].ffill()

# Remove Duplicate Rows
print("\n-- Calculate nav null value --")
print(df.duplicated().sum())

# Drop Duplicated Value
df = df.drop_duplicates()

# validate NAV <= 0
print("\n-- Nav <= 0 --")
print(df[df["nav"] <= 0])

# validate NAV > 0
df = df[df["nav"] > 0]

# Save the Cleaned File
df.to_csv("../data/processed/nav_history.csv", index=False)


print("\nCleaning completed successfully!")