import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dashboard.utils.db import get_peers,get_companies,get_ratios
from analytics.peer import METRICS

st.title('Peer Comparison')
companies=get_companies(); groups=sorted(get_peers.__wrapped__ if False else [])
# Discover groups directly from database through companies helper's SQL utility.
from dashboard.utils.db import _read_sql
pg=_read_sql('SELECT DISTINCT peer_group_name FROM peer_groups ORDER BY peer_group_name')
group=st.selectbox('Peer group',pg.peer_group_name.tolist() if not pg.empty else [])
peers=get_peers(group) if group else pd.DataFrame()
if peers.empty: st.info('No peer data available.'); st.stop()
ticker=st.selectbox('Company',peers.company_id.astype(str).tolist())
rows=[]
for t in peers.company_id.astype(str):
    r=get_ratios(t)
    if not r.empty: rows.append(r.iloc[-1].to_dict())
metric_map={'ROE':'return_on_equity_pct','ROCE':'roce_pct','Net Profit Margin':'net_profit_margin_pct','D/E':'debt_to_equity','FCF':'free_cash_flow_cr','PAT CAGR 5yr':'pat_cagr_5yr','Revenue CAGR 5yr':'revenue_cagr_5yr','EPS CAGR 5yr':'eps_cagr_5yr','Interest Coverage':'interest_coverage','Asset Turnover':'asset_turnover'}
base=pd.DataFrame(rows); selected=base[base.company_id.astype(str)==ticker]
if selected.empty: st.info('Selected company has no ratio data.'); st.stop()
peerbase=base[base.company_id.astype(str).isin(peers.company_id.astype(str))]
r=selected.iloc[0]; avg=peerbase.mean(numeric_only=True)
labels=list(metric_map); v=[pd.to_numeric(r.get(c),errors='coerce') for c in metric_map.values()]; a=[pd.to_numeric(avg.get(c),errors='coerce') for c in metric_map.values()]
# Normalize each axis to a comparable 0-100 score for visualization.
import numpy as np
def norm(vals):
    z=pd.to_numeric(pd.Series(vals),errors='coerce'); lo=z.min(); hi=z.max(); return [50 if pd.isna(x) else (50 if hi==lo else (x-lo)/(hi-lo)*100) for x in z]
fig=go.Figure(); fig.add_trace(go.Scatterpolar(r=norm(v),theta=labels,fill='toself',name=ticker)); fig.add_trace(go.Scatterpolar(r=norm(a),theta=labels,line=dict(dash='dash'),name='Peer average')); fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])),showlegend=True)
st.plotly_chart(fig,use_container_width=True)
st.subheader('Peer companies')
display=peers.copy(); display['Benchmark']=display['is_benchmark'].map({1:'⭐ Benchmark',0:''}).fillna('')
st.dataframe(display[['company_id','company_name','Benchmark']],use_container_width=True,hide_index=True)
