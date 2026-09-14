import io
import pandas as pd
import streamlit as st
from dashboard.utils.db import get_companies,get_ratios
from screener.engine import run_all, load_universe, apply_filters

st.title('Screener')
base=load_universe()
if base.empty: st.warning('No screener universe available.'); st.stop()

with st.sidebar:
    st.subheader('Filters')
    vals={
      'roe_min':st.slider('ROE min',0.0,50.0,0.0), 'de_max':st.slider('D/E max',0.0,10.0,10.0),
      'fcf_min':st.slider('FCF min (Cr)',-5000.0,5000.0, -5000.0), 'revenue_cagr_5yr_min':st.slider('Revenue CAGR 5yr min',-50.0,50.0, -50.0),
      'pat_cagr_5yr_min':st.slider('PAT CAGR 5yr min',-50.0,100.0,-50.0), 'opm_min':st.slider('OPM min',-50.0,100.0,-50.0),
      'pe_max':st.slider('P/E max',0.0,150.0,150.0), 'pb_max':st.slider('P/B max',0.0,30.0,30.0),
      'dividend_yield_min':st.slider('Dividend Yield min',0.0,15.0,0.0), 'icr_min':st.slider('ICR min',0.0,20.0,0.0)
    }
    if st.button('Reset filters'): st.rerun()

preset=st.selectbox('Preset', ['Custom','Quality Compounder','Value Pick','Growth Accelerator','Dividend Champion','Debt-Free Blue Chip','Turnaround Watch'])
if preset!='Custom':
    try: result=run_all().get(preset,pd.DataFrame())
    except Exception as e: st.error(str(e)); result=pd.DataFrame()
else:
    result=apply_filters(base,vals)

st.write(f'**{len(result)} companies match your filters**')
visible=[c for c in ['company_id','company_name','broad_sector','composite_quality_score','roe','roce','npm','de','fcf','revenue_cagr_5yr','pat_cagr_5yr','opm','pe_ratio','pb_ratio','dividend_yield_pct','icr'] if c in result.columns]
st.dataframe(result[visible].sort_values('composite_quality_score',ascending=False) if visible else result,use_container_width=True,hide_index=True)
st.download_button('Download CSV',result[visible if visible else list(result.columns)].to_csv(index=False).encode('utf-8'),'screener_results.csv','text/csv')
