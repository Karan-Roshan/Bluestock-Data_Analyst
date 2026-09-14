from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / 'nifty100.db'
RAW_MARKET_CAP = ROOT / 'data' / 'raw' / 'market_cap.xlsx'


def _read_sql(sql, params=()):
    if not DB_PATH.exists():
        return pd.DataFrame()
    with sqlite3.connect(DB_PATH) as con:
        return pd.read_sql_query(sql, con, params=params)

@st.cache_data(ttl=600)
def get_companies():
    return _read_sql('SELECT * FROM companies ORDER BY company_name')

@st.cache_data(ttl=600)
def get_ratios(ticker, year=None):
    if year is None:
        return _read_sql('SELECT * FROM financial_ratios WHERE company_id=? ORDER BY period', (ticker,))
    return _read_sql('SELECT * FROM financial_ratios WHERE company_id=? AND period=?', (ticker, year))

@st.cache_data(ttl=600)
def get_pl(ticker):
    return _read_sql('SELECT * FROM profitandloss WHERE company_id=? ORDER BY period', (ticker,))

@st.cache_data(ttl=600)
def get_bs(ticker):
    return _read_sql('SELECT * FROM balancesheet WHERE company_id=? ORDER BY period', (ticker,))

@st.cache_data(ttl=600)
def get_cf(ticker):
    return _read_sql('SELECT * FROM cashflow WHERE company_id=? ORDER BY period', (ticker,))

@st.cache_data(ttl=600)
def get_sectors():
    return _read_sql('SELECT * FROM sectors ORDER BY 1')

@st.cache_data(ttl=600)
def get_peers(group_name):
    return _read_sql('''SELECT p.*, c.company_name, c.broad_sector
                        FROM peer_groups p LEFT JOIN companies c ON c.company_id=p.company_id
                        WHERE p.peer_group_name=? ORDER BY p.is_benchmark DESC, c.company_name''', (group_name,))

@st.cache_data(ttl=600)
def get_valuation(ticker):
    # market_cap SQLite contains core fields; raw Excel contains valuation multiples.
    q = _read_sql('SELECT * FROM market_cap WHERE company_id=? ORDER BY period', (ticker,))
    if RAW_MARKET_CAP.exists():
        try:
            raw = pd.read_excel(RAW_MARKET_CAP, header=1)
            raw.columns = [str(c).strip() for c in raw.columns]
            raw = raw.rename(columns={'id':'row_id'})
            raw = raw[raw['company_id'].astype(str) == str(ticker)]
            if not raw.empty:
                return raw
        except Exception:
            pass
    return q
