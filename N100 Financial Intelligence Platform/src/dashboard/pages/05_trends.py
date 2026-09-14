import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dashboard.utils.db import get_companies,get_ratios

st.title('Trend Analysis')
companies=get_companies(); labels=(companies.company_name.fillna('')+' — '+companies.company_id.astype(str)).tolist(); choice=st.selectbox('Company',labels); ticker=choice.rsplit(' — ',1)[-1]
r=get_ratios(ticker)
if r.empty: st.info('No historical data available.'); st.stop()
metric_cols={'Revenue':'sales','Net Profit':'net_profit','EPS':'eps','ROE':'return_on_equity_pct','ROCE':'roce_pct','FCF':'free_cash_flow_cr','D/E':'debt_to_equity','OPM':'operating_profit_margin_pct'}
selected=st.multiselect('Metrics (up to 3)',list(metric_cols),default=['Revenue','Net Profit'])[:3]
fig=go.Figure(); rr=r.copy(); rr['period']=pd.to_numeric(rr.period,errors='coerce'); rr=rr.tail(10)
for name in selected:
    c=metric_cols[name]; y=pd.to_numeric(rr.get(c),errors='coerce'); fig.add_trace(go.Scatter(x=rr.period,y=y,mode='lines+markers',name=name,customdata=y.pct_change().mul(100),hovertemplate='%{x}: %{y:.2f}<br>YoY: %{customdata:.2f}%'))
fig.update_layout(hovermode='x unified'); st.plotly_chart(fig,use_container_width=True)
