
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from screener.engine import run_all
from analytics.peer import compute_percentiles,make_radar_charts
from reports import write_screener,write_peer_comparison
if __name__=="__main__":
    print("=== Sprint 3 Screener ===")
    for n,d in run_all().items(): print(f"{n}: {len(d)} companies")
    print("=== Peer Percentiles ===")
    p=compute_percentiles(); print(f"Rows: {len(p)} | Groups: {p.peer_group_name.nunique() if len(p) else 0}")
    print("=== Excel Reports ==="); print(write_screener()); print(write_peer_comparison())
    print("=== Radar Charts ==="); print(f"Created: {make_radar_charts()}")
