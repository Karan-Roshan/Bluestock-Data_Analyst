import pandas as pd

df = pd.read_csv("../data/raw/investor_transactions.csv")

# View the first few rows
print("\n-- First five rows --")
print(df.head(5))

# Check the dataset information
print("\n-- Dataset information --")
print(df.info())

# Standardize transaction_type
df["transaction_type"] = df["transaction_type"].str.strip();        # remove extra spaces

df["transaction_type"] = df["transaction_type"].str.title();        # Convert to title case

df["transaction_type"] = df["transaction_type"].replace({
    "Sip": "SIP",
    "Lump Sum": "Lumpsum",
    "Lumpsum": "Lumpsum",
    "Redemption": "Redemption"
})

print(df["transaction_type"].unique())

# validate NAV <= 0
print("\n-- Amount <= 0 --")
print(df[df["amount_inr"] <= 0])

# Remove Amount > 0
df = df[df["amount_inr"] > 0].reset_index(drop=True)

print("\n-- Minimum Amount <= 0 --")
print("Minimum Amount: ", df["amount_inr"].min()) 

# Convert Date to Datetime
df["transaction_date"] = pd.to_datetime(df["transaction_date"])

print("\n-- Datatype of Date <= 0 --")
print("Datatype of Date: ", df["transaction_date"].dtype) 

# Validate KYC Status Values
print("\n-- KYC Status --")
print(df["kyc_status"].unique())

df["kyc_status"] = df["kyc_status"].str.strip().str.title()     #Standardize

print("\n-- KYC Status --")
print(df["kyc_status"].unique())



# Save the Cleaned File
df.to_csv("../data/raw/investor_transactions.csv", index=False)

print("\nInvestor transactions cleaned successfully!")