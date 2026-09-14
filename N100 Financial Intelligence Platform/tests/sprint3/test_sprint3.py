
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"src"))
import pandas as pd
from screener.engine import apply_filters,add_composite_score
from analytics.peer import METRICS

def test_all_ten_peer_metrics():
    assert len(METRICS)==10

def test_composite_is_0_to_100():
    d=pd.DataFrame({"roe":[10,20,30],"roce":[10,20,30],"npm":[5,10,15],"de":[3,2,1],
                    "fcf":[1,2,3],"revenue_cagr_5yr":[5,10,15],"pat_cagr_5yr":[5,10,20],"icr":[1,2,3]})
    assert add_composite_score(d).composite_quality_score.between(0,100).all()

def test_financials_are_exempt_from_de_max():
    d=pd.DataFrame({"company_id":["A","B"],"broad_sector":["Financials","IT"],"de":[5,.5]})
    assert set(apply_filters(d,{"debt_to_equity_max":1}).company_id)=={"A","B"}
