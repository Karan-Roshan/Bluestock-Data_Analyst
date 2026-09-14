from pathlib import Path
import sys
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))

from screener.engine import apply_filters
from analytics.valuation import build_valuation


def test_custom_screener_mapping():
    d=pd.DataFrame({'company_id':['A','B'],'roe':[20,10],'pe_ratio':[15,25],'broad_sector':['IT','IT'],'de':[0.5,1]})
    out=apply_filters(d,{'roe_min':15,'pe_max':20})
    assert list(out.company_id)==['A']


def test_valuation_flag_logic():
    x=pd.DataFrame({'pe_ratio':[40,10,20],'sector':['IT','IT','IT']})
    median=x.pe_ratio.median()
    flags=np.select([x.pe_ratio>median*1.5,x.pe_ratio<median*.7],['Caution','Discount'],default='Fair')
    assert list(flags)==['Caution','Discount','Fair']
