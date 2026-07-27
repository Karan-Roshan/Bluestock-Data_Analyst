import requests
import pandas as pd

# Fetch - HDFC_Top100_NAV.csv
"""
url = "https://api.mfapi.in/mf/125497"

response = requests.get(url)
data = response.json()

# print(data.keys())

nav = pd.DataFrame(data["data"])
print(nav.head())

nav.to_csv("../data/raw/HDFC_Top100_NAV.csv", index=False)
"""

# Fetch 5 Mutual Funds
funds = {
    "HDFC":125497,
    "SBI":119551,
    "ICICI":120503,
    "Nippon":118632,
    "Axis":119092,
    "Kotak":120841
}

for name, code in funds.items():
    url = f"https://api.mfapi.in/mf/{code}"

    response = requests.get(url)

    data = response.json()

    df = pd.DataFrame(data["data"])

    df.to_csv (f"../data/raw/{name}.csv", index=False)

    print(name, "Downloaded")