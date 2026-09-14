
"""Sprint 3 peer percentile rankings and radar charts."""

from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd

from screener.engine import load_universe, add_composite_score

ROOT=Path(__file__).resolve().parents[2]
DB=ROOT/"nifty100.db"
REPORTS=ROOT/"reports/radar_charts"
REPORTS.mkdir(parents=True,exist_ok=True)

# (dataframe column, inverse_metric)
METRICS={
"ROE":("roe",False),
"ROCE":("roce",False),
"Net Profit Margin":("npm",False),
"D/E":("de",True),
"FCF":("fcf",False),
"PAT CAGR 5yr":("pat_cagr_5yr",False),
"Revenue CAGR 5yr":("revenue_cagr_5yr",False),
"EPS CAGR 5yr":("eps_cagr_5yr",False),
"Interest Coverage":("icr",False),
"Asset Turnover":("asset_turnover",False),
}

def _peers(db_path=DB):
    c=sqlite3.connect(db_path)
    try: return pd.read_sql("select company_id, group_name, sector_name from peer_groups",c)
    finally: c.close()

def compute_percentiles(db_path=DB):
    base,_,_=load_universe(db_path)
    base=add_composite_score(base)
    peers=_peers(db_path)
    peers=peers.dropna(subset=["company_id","group_name"]).drop_duplicates(["company_id","group_name"])
    x=base.merge(peers[["company_id","group_name"]],on="company_id",how="inner")
    records=[]
    for group,g in x.groupby("group_name"):
        for label,(col,inverse) in METRICS.items():
            if col not in g: continue
            vals=pd.to_numeric(g[col],errors="coerce")
            valid=vals.notna()
            if not valid.any(): continue
            pct=vals.rank(method="min",pct=True)
            if inverse: pct=1-pct
            for i in g.index[valid]:
                records.append((g.loc[i,"company_id"],group,label,float(vals.loc[i]),float(pct.loc[i]),None))
    out=pd.DataFrame(records,columns=["company_id","peer_group_name","metric","value","percentile_rank","year"])
    c=sqlite3.connect(db_path)
    try:
        c.execute("""create table if not exists peer_percentiles(
        company_id text not null, peer_group_name text not null, metric text not null,
        value real, percentile_rank real, year integer,
        primary key(company_id,peer_group_name,metric,year),
        foreign key(company_id) references companies(company_id))""")
        c.execute("delete from peer_percentiles")
        if not out.empty:
            c.executemany("insert into peer_percentiles values(?,?,?,?,?,?)",out.itertuples(index=False,name=None))
        c.commit()
    finally: c.close()
    return out

def make_radar_charts(db_path=DB):
    import matplotlib.pyplot as plt
    base,_,_=load_universe(db_path); base=add_composite_score(base); peers=_peers(db_path)
    x=base.merge(peers[["company_id","group_name"]].drop_duplicates("company_id"),on="company_id",how="left")
    axes=["roe","roce","npm","de","fcf","pat_cagr_5yr","revenue_cagr_5yr","composite_quality_score"]
    labels=["ROE","ROCE","NPM","D/E","FCF","PAT CAGR","Revenue CAGR","Composite"]
    count=0
    for _,r in x.iterrows():
        group=r.group_name if pd.notna(r.group_name) else None
        ref=x[x.group_name==group][axes].mean(numeric_only=True) if group else x[axes].mean(numeric_only=True)
        vals=pd.to_numeric(r[axes],errors="coerce").fillna(0).tolist()
        refs=pd.to_numeric(ref,errors="coerce").fillna(0).tolist()
        peer=x[x.group_name==group][axes] if group else x[axes]
        sv=[]; sr=[]
        for a,v,rv in zip(axes,vals,refs):
            lo,hi=pd.to_numeric(peer[a],errors="coerce").quantile(.10),pd.to_numeric(peer[a],errors="coerce").quantile(.90)
            if pd.isna(lo) or pd.isna(hi) or hi==lo: sv.append(.5); sr.append(.5)
            else: sv.append(float(np.clip((v-lo)/(hi-lo),0,1))); sr.append(float(np.clip((rv-lo)/(hi-lo),0,1)))
        angles=np.linspace(0,2*np.pi,len(axes),endpoint=False).tolist()
        sv+=sv[:1]; sr+=sr[:1]; angles+=angles[:1]
        fig=plt.figure(figsize=(7,7)); ax=fig.add_subplot(111,polar=True)
        ax.plot(angles,sv,linewidth=2); ax.fill(angles,sv,alpha=.18)
        ax.plot(angles,sr,linestyle="--",linewidth=1.5)
        ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels,fontsize=9)
        ax.set_title(f"{r.company_id} — {group or 'Nifty 100 average'}",pad=20)
        fig.tight_layout(); fig.savefig(REPORTS/f"{r.company_id}_radar.png",dpi=150); plt.close(fig); count+=1
    return count

if __name__=="__main__":
    p=compute_percentiles(); print(f"Peer percentile rows created: {len(p)}"); print(f"Peer groups: {p.peer_group_name.nunique() if len(p) else 0}"); print(f"Radar charts: {make_radar_charts()}")
