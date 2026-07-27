import pandas as pd
import os

DATA_FOLDER = "../data/raw"

# List all CSVs
csv_file = []

for file in os.listdir(DATA_FOLDER):
    if file.endswith(".csv"):
        csv_file.append(file)

print(csv_file)

# Read Every CSV File
for file in csv_file:
    path = os.path.join(DATA_FOLDER, file)

    df = pd.read_csv(path)

    print("=" * 50)
    print(file)
    print("=" * 50)

    print("\n-- Shape --")
    print(df.shape)

    print("\n-- Data Types --")
    print(df.dtypes)

    print("\n-- First Five Rows --")
    print(df.head(5))

    print("\n-- Missing Values --")
    print(df.isnull().sum())

    print("\n")


# Explore fund_master.csv
fund_master = pd.read_csv("../data/raw/fund_master.csv")

print("\n-- Unique Fund Houses --")
print(fund_master["fund_house"].unique())

print("\n-- Count --")
print(fund_master["fund_house"].nunique())

print("\n-- Categories --")
print(fund_master["category"].unique())

print("\n-- Sub Categories --")
print(fund_master["sub_category"].unique())

print("\n-- Risk Grades --")
print(fund_master["risk_category"].unique())


# Validate AMFI codes 
master = pd.read_csv("../data/raw/fund_master.csv")

history = pd.read_csv("../data/raw/nav_history.csv")

master_code = set(master["amfi_code"])
history_code = set(history["amfi_code"])

missing = master_code - history_code

print("\n-- Missing --")
print("Missing Length:", len(missing))