from pathlib import Path
import runpy
import sys
import streamlit as st

SRC = Path(__file__).resolve().parents[1]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

st.set_page_config(page_title='Nifty 100 Analytics', layout='wide', initial_sidebar_state='expanded')

PAGES = {
    '01 — Home': '01_home.py', '02 — Profile': '02_profile.py', '03 — Screener': '03_screener.py',
    '04 — Peers': '04_peers.py', '05 — Trends': '05_trends.py', '06 — Sectors': '06_sectors.py',
    '07 — Capital': '07_capital.py', '08 — Reports': '08_reports.py'
}

st.sidebar.title('Nifty 100 Analytics')
page = st.sidebar.radio('Navigate', list(PAGES))
st.sidebar.caption('Sprint 4 • Financial Intelligence Platform')

page_path = Path(__file__).parent / 'pages' / PAGES[page]
runpy.run_path(str(page_path), run_name='__main__')
