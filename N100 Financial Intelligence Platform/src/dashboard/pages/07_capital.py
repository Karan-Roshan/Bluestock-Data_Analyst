import pandas as pd
import plotly.express as px
import streamlit as st
from dashboard.utils.db import get_companies,get_ratios

st.title('Capital Allocation Map')
c=get_companies(); rows=[]
for t in c.company_id.astype(str):
    r=get_ratios(t)
    if not r.empty:
        d=r.iloc[-1].to_dict(); d['company_id']=t; rows.append(d)
df=pd.DataFrame(rows).merge(c[['company_id','company_name']],on='company_id',how='left')
pattern_col=next((x for x in ['capital_allocation_pattern','capital_allocation','allocation_pattern'] if x in df.columns),None)
if pattern_col is None:
    def classify(r):
        f=float(r.get('free_cash_flow_cr') or 0); dp=float(r.get('dividend_payout_ratio_pct') or 0); debt=float(r.get('debt_to_equity') or 0)
        if f>0 and dp>=60:return 'Dividend / Shareholder Return'
        if f>0 and debt<1:return 'FCF Reinvestment'
        if debt>2:return 'Debt-Funded / Leveraged'
        return 'Balanced / Other'
    df['pattern']=df.apply(classify,axis=1); pattern_col='pattern'
agg=df.groupby(pattern_col).size().reset_index(name='companies'); fig=px.treemap(agg,path=[pattern_col],values='companies'); event=st.plotly_chart(fig,use_container_width=True,on_select='rerun',selection_mode='points')
pat=st.selectbox('View companies in pattern',agg[pattern_col].tolist()); st.dataframe(df[df[pattern_col]==pat][['company_id','company_name']],use_container_width=True,hide_index=True)
