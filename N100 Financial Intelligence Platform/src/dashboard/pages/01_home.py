import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path
from dashboard.utils.db import get_companies, get_ratios

st.title('Nifty 100 Analytics')
companies = get_companies()
year = st.sidebar.selectbox('Analysis year', list(range(2024, 2018, -1)), index=0)

if companies.empty:
    st.error('Database not found or no companies loaded. Run Sprint 1 loader first.')
    st.stop()

rows=[]
for t in companies.company_id.astype(str):
    r=get_ratios(t, year)
    if not r.empty: rows.append(r.iloc[-1].to_dict())
rat=pd.DataFrame(rows)
for c in ['return_on_equity_pct','roce_pct','debt_to_equity','revenue_cagr_5yr']:
    if c not in rat: rat[c]=np.nan

# Valuation multiples are loaded from the raw market-cap file by the valuation module; keep home robust.
valuation_file = Path(__file__).resolve().parents[3] / 'output' / 'valuation_summary.xlsx'
median_pe = np.nan
if valuation_file.exists():
    try:
        vv = pd.read_excel(valuation_file)
        median_pe = pd.to_numeric(vv.get('P/E'), errors='coerce').median()
    except Exception:
        pass

summary = pd.DataFrame({
    'Average ROE':[pd.to_numeric(rat.return_on_equity_pct, errors='coerce').mean()],
    'Median P/E':[median_pe], 'Median D/E':[pd.to_numeric(rat.debt_to_equity, errors='coerce').median()],
    'Total Companies':[len(companies)], 'Median Revenue CAGR 5yr':[pd.to_numeric(rat.revenue_cagr_5yr, errors='coerce').median()],
    'Debt-Free Companies':[(pd.to_numeric(rat.debt_to_equity, errors='coerce').fillna(np.nan) == 0).sum()]
})
cols=st.columns(6)
for col, name in zip(cols, summary.columns): col.metric(name, 'N/A' if pd.isna(summary.iloc[0][name]) else (f"{summary.iloc[0][name]:,.2f}" if name!='Total Companies' else f"{int(summary.iloc[0][name])}"))

st.subheader('Sector breakdown')
sec=companies.copy()
sector_col='broad_sector' if 'broad_sector' in sec else ('sector_id' if 'sector_id' in sec else None)
if sector_col:
    counts=sec[sector_col].fillna('Unknown').value_counts().reset_index(); counts.columns=['sector','companies']
    st.plotly_chart(px.pie(counts,names='sector',values='companies',hole=.55),use_container_width=True)

st.subheader('Top 5 Composite Quality')
if 'composite_quality_score' in rat:
    top=rat.merge(companies[['company_id','company_name']],on='company_id',how='left').sort_values('composite_quality_score',ascending=False).head(5)
    st.dataframe(top[['company_id','company_name','composite_quality_score']],use_container_width=True,hide_index=True)
else:
    st.info('Composite scores are available after Sprint 3 outputs are generated.')
