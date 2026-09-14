import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from dashboard.utils.db import get_companies,get_ratios,get_pl,get_bs,get_cf

st.title('Company Profile')
companies=get_companies()
if companies.empty: st.error('No company data available.'); st.stop()
labels=(companies.company_name.fillna('')+' — '+companies.company_id.astype(str)).tolist()
choice=st.selectbox('Search company or ticker',labels)
ticker=str(choice.rsplit(' — ',1)[-1])
c=companies[companies.company_id.astype(str)==ticker].iloc[0]

st.subheader(str(c.get('company_name',ticker)))
st.caption(f"Ticker: {ticker}  •  Sector: {c.get('broad_sector','N/A')}  •  Sub-sector: {c.get('sector_id','N/A')}")
st.write(c.get('about_company','') or 'No company description available.')

r=get_ratios(ticker); p=get_pl(ticker)
latest=r.iloc[-1] if not r.empty else pd.Series(dtype=object)
def val(col):
    x=latest.get(col,np.nan); return 'N/A' if pd.isna(x) else f'{float(x):,.2f}'
cols=st.columns(6)
for col,title,key in zip(cols,['ROE','ROCE','Net Profit Margin','D/E','Revenue CAGR 5yr','FCF'],['return_on_equity_pct','roce_pct','net_profit_margin_pct','debt_to_equity','revenue_cagr_5yr','free_cash_flow_cr']): col.metric(title,val(key))

if not p.empty:
    chart=p.copy(); chart['period']=pd.to_numeric(chart['period'],errors='coerce'); chart['sales']=pd.to_numeric(chart['sales'],errors='coerce'); chart['net_profit']=pd.to_numeric(chart['net_profit'],errors='coerce')
    chart=chart.tail(10)
    st.plotly_chart(px.bar(chart,x='period',y=['sales','net_profit'],barmode='group',labels={'value':'Cr'}),use_container_width=True)

rr=r.copy(); rr['period']=pd.to_numeric(rr['period'],errors='coerce')
if not rr.empty:
    fig=go.Figure(); fig.add_trace(go.Scatter(x=rr.period,y=rr.return_on_equity_pct,name='ROE')); fig.add_trace(go.Scatter(x=rr.period,y=rr.roce_pct,name='ROCE',yaxis='y2')); fig.update_layout(yaxis=dict(title='ROE'),yaxis2=dict(title='ROCE',overlaying='y',side='right')); st.plotly_chart(fig,use_container_width=True)

st.subheader('Pros & Cons')
pros=[]; cons=[]
# Best-effort lookup because source schemas vary between datasets.
try:
    from dashboard.utils.db import _read_sql
    pc=_read_sql('SELECT * FROM prosandcons WHERE company_id=?',(ticker,))
    for _,row in pc.iterrows():
        text=' '.join(str(v) for v in row.tolist() if pd.notna(v) and str(v)!=ticker)
        if any(k in text.lower() for k in ['cons','risk','weak','negative']): cons.append(text)
        else: pros.append(text)
except Exception: pass
st.markdown('\n'.join('✅ '+x for x in pros[:10]) or 'No pros available.')
st.markdown('\n'.join('❌ '+x for x in cons[:10]) or 'No cons available.')
