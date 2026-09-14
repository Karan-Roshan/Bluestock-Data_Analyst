import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from dashboard.utils.db import get_companies,get_ratios,_read_sql

st.title('Sector Analysis')
c=get_companies(); sector_col='broad_sector' if 'broad_sector' in c else 'sector_id'; sectors=sorted(c[sector_col].dropna().astype(str).unique()); sector=st.selectbox('Sector',sectors)
rows=[]
for t in c[c[sector_col].astype(str)==sector].company_id.astype(str):
    r=get_ratios(t)
    if not r.empty:
        d=r.iloc[-1].to_dict(); d['company_id']=t; rows.append(d)
df=pd.DataFrame(rows)
if df.empty: st.info('No data for this sector.'); st.stop()
mc=_read_sql('SELECT company_id,period,market_cap FROM market_cap')
if not mc.empty: df=df.merge(mc.sort_values('period').groupby('company_id').tail(1)[['company_id','market_cap']],on='company_id',how='left')
else: df['market_cap']=1
names=c[['company_id','company_name']]; df=df.merge(names,on='company_id',how='left'); df['sub_sector']=sector
fig=px.scatter(df,x='sales',y='return_on_equity_pct',size='market_cap',color='sub_sector',hover_name='company_name'); fig.update_layout(xaxis_title='Revenue (Cr)',yaxis_title='ROE %'); st.plotly_chart(fig,use_container_width=True)
med=df[['return_on_equity_pct','roce_pct','net_profit_margin_pct','debt_to_equity']].apply(pd.to_numeric,errors='coerce').median().reset_index(); med.columns=['metric','median']; st.plotly_chart(px.bar(med,x='metric',y='median',title='Sector median KPIs'),use_container_width=True)
