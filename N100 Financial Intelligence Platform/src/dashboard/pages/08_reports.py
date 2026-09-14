import pandas as pd
import requests
import streamlit as st
from dashboard.utils.db import get_companies,_read_sql

st.title('Annual Reports')
c=get_companies(); labels=(c.company_name.fillna('')+' — '+c.company_id.astype(str)).tolist(); choice=st.selectbox('Company',labels); ticker=choice.rsplit(' — ',1)[-1]
try:
    docs=_read_sql('SELECT * FROM documents WHERE company_id=? ORDER BY 1 DESC',(ticker,))
except Exception: docs=pd.DataFrame()
if docs.empty: st.info('No annual report records available for this company.'); st.stop()
url_col=next((x for x in docs.columns if 'url' in x.lower() or 'link' in x.lower()),None); year_col=next((x for x in docs.columns if 'year' in x.lower() or 'period' in x.lower()),None)
if url_col is None: st.dataframe(docs,use_container_width=True,hide_index=True); st.stop()
for _,row in docs.iterrows():
    year=row.get(year_col,'Report'); url=row.get(url_col)
    if pd.isna(url) or not str(url).startswith(('http://','https://')): st.write(f'{year} — 🔴 Report unavailable'); continue
    try:
        ok=requests.head(str(url),timeout=3,allow_redirects=True).status_code < 400
    except Exception: ok=False
    if ok: st.markdown(f'**{year}** — [Open BSE PDF]({url})')
    else: st.write(f'{year} — 🔴 Report unavailable')
