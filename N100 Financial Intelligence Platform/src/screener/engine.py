
"""Sprint 3 screener engine built for the real N100 Sprint 1/2 data model."""

from pathlib import Path
import sqlite3
import math
import re
import pandas as pd
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "nifty100.db"
RAW = ROOT / "data" / "raw"
CONFIG = ROOT / "config" / "screener_config.yaml"

PRESETS = [
    "Quality Compounder", "Value Pick", "Growth Accelerator",
    "Dividend Champion", "Debt-Free Blue Chip", "Turnaround Watch"
]

def _clean(v):
    if pd.isna(v): return None
    s = str(v).strip()
    return s if s and s.lower() != "nan" else None

def _year(v):
    s = _clean(v)
    if not s: return None
    m = re.search(r"(19|20)\d{2}", s)
    return int(m.group()) if m else None

def _read_raw(name, header=0):
    p = RAW / name
    if not p.exists():
        return pd.DataFrame()
    return pd.read_excel(p, header=header)

def load_config():
    with open(CONFIG, encoding="utf-8") as f:
        return yaml.safe_load(f)

def _latest(df, group="company_id"):
    if df.empty: return df
    x=df.copy()
    x["year_num"]=x["year"].map(_year) if "year" in x else np.nan
    x=x.dropna(subset=[group]).sort_values(["year_num"])
    return x.groupby(group, as_index=False).tail(1).drop(columns=["year_num"], errors="ignore")

def _cagr(hist, value_col, years):
    rows=[]
    if hist.empty: return pd.DataFrame(columns=["company_id", f"{value_col}_cagr_{years}yr"])
    for cid,g in hist.groupby("company_id"):
        g=g.copy()
        g["yr"]=g["year"].map(_year)
        g=g.dropna(subset=["yr"]).sort_values("yr")
        if len(g)<2: continue
        latest=g.iloc[-1]
        target=latest["yr"]-years
        candidates=g[g["yr"]<=target]
        if candidates.empty: continue
        base=candidates.iloc[-1]
        v0=pd.to_numeric(base[value_col],errors="coerce")
        v1=pd.to_numeric(latest[value_col],errors="coerce")
        elapsed=latest["yr"]-base["yr"]
        if pd.notna(v0) and pd.notna(v1) and v0>0 and v1>0 and elapsed>0:
            rows.append((cid,((v1/v0)**(1/elapsed)-1)*100))
    return pd.DataFrame(rows,columns=["company_id",f"{value_col}_cagr_{years}yr"])

def load_universe(db_path=DB):
    con=sqlite3.connect(db_path)
    try:
        co=pd.read_sql("SELECT * FROM companies",con)
        fr=pd.read_sql("SELECT * FROM financial_ratios",con)
        pnl=pd.read_sql("SELECT * FROM profitandloss",con)
        bs=pd.read_sql("SELECT * FROM balancesheet",con)
        cf=pd.read_sql("SELECT * FROM cashflow",con)
    finally: con.close()

    # Company-provided files contain ROE/ROCE source values and valuation metrics.
    raw_co=_read_raw("companies.xlsx", header=1)
    if not raw_co.empty:
        raw_co.columns=[str(c).strip().lower() for c in raw_co.columns]
        raw_co=raw_co.rename(columns={"id":"company_id"})
        keep=[c for c in ["company_id","roe_percentage","roce_percentage","broad_sector"] if c in raw_co]
        co=co.merge(raw_co[keep].drop_duplicates("company_id"),on="company_id",how="left",suffixes=("","_raw"))

    mc=_read_raw("market_cap.xlsx", header=0)
    if not mc.empty:
        mc.columns=[str(c).strip().lower() for c in mc.columns]
        mc["year"]=pd.to_numeric(mc["year"],errors="coerce")
        mc=_latest(mc)
        mc=mc.rename(columns={
            "market_cap_crore":"market_cap",
            "market_cap":"market_cap",
            "pe":"pe_ratio",
            "p_e":"pe_ratio",
            "pb":"pb_ratio",
            "p_b":"pb_ratio",
            "dividend_yield":"dividend_yield_pct",
            "dividend_yield_percentage":"dividend_yield_pct",
        })
        for col in ["market_cap","pe_ratio","pb_ratio","dividend_yield_pct"]:
            if col not in mc.columns:
                mc[col] = np.nan
        mc=mc[["company_id","market_cap","pe_ratio","pb_ratio","dividend_yield_pct"]]

    for x in [pnl,bs,cf,fr]:
        if "year" in x: x["year_num"]=x["year"].map(_year)

    pl=_latest(pnl); b=_latest(bs); c=_latest(cf); r=_latest(fr)
    cols=["company_id","company_name","broad_sector","roe_percentage","roce_percentage"]
    cols=[x for x in cols if x in co.columns]
    out=co[cols].drop_duplicates("company_id")
    # The unified Sprint 1/2 schema stores dividend amount as `dividend`,
    # while the company source P&L also has `dividend_payout` percentage.
    # Use whichever is available and derive payout % when only dividend amount exists.
    pl_cols = ["company_id", "year", "sales", "net_profit",
               "operating_profit", "interest", "eps"]
    if "dividend_payout" in pl.columns:
        pl_cols.append("dividend_payout")
    if "dividend" in pl.columns:
        pl_cols.append("dividend")
    pl_latest = pl[pl_cols].copy()
    if "dividend_payout" not in pl_latest.columns:
        pl_latest["dividend_payout"] = np.nan
    if "dividend" in pl_latest.columns:
        payout_calc = (
            pd.to_numeric(pl_latest["dividend"], errors="coerce") /
            pd.to_numeric(pl_latest["net_profit"], errors="coerce").replace(0, np.nan) * 100
        )
        pl_latest["dividend_payout"] = pl_latest["dividend_payout"].fillna(payout_calc)
    out=out.merge(pl_latest,on="company_id",how="left")
    out=out.merge(b[["company_id","borrowings","equity_capital","reserves","total_assets"]],on="company_id",how="left")
    # The unified Sprint 1/2 cash-flow schema uses `cash_from_operating`
    # and `cash_from_investing`, not the source-file activity labels.
    cf_cols = ["company_id"]
    for source_name, target_name in [
        ("cash_from_operating", "operating_activity"),
        ("cash_from_investing", "investing_activity"),
    ]:
        if source_name in c.columns:
            c = c.rename(columns={source_name: target_name})
        if target_name not in c.columns:
            c[target_name] = np.nan
        cf_cols.append(target_name)
    out=out.merge(c[cf_cols],on="company_id",how="left")
    if not r.empty:
        rcols=[x for x in ["company_id","return_on_equity_pct","roce_pct","net_profit_margin_pct",
                           "operating_profit_margin_pct","debt_to_equity","interest_coverage",
                           "asset_turnover","free_cash_flow_cr","pat_cagr_5yr","revenue_cagr_5yr",
                           "eps_cagr_5yr","revenue_cagr_3yr","composite_quality_score"] if x in r]
        out=out.merge(r[rcols],on="company_id",how="left",suffixes=("","_ratio"))

    out["roe"]=pd.to_numeric(out.get("return_on_equity_pct"),errors="coerce")
    if "roe_percentage" in out: out["roe"]=out["roe"].fillna(pd.to_numeric(out["roe_percentage"],errors="coerce"))
    out["roce"]=pd.to_numeric(out.get("roce_pct"),errors="coerce")
    if "roce_percentage" in out: out["roce"]=out["roce"].fillna(pd.to_numeric(out["roce_percentage"],errors="coerce"))
    out["sales"]=pd.to_numeric(out["sales"],errors="coerce")
    out["net_profit"]=pd.to_numeric(out["net_profit"],errors="coerce")
    out["npm"]=out["net_profit"]/out["sales"].replace(0,np.nan)*100
    out["opm"]=pd.to_numeric(out["operating_profit"],errors="coerce")/out["sales"].replace(0,np.nan)*100
    out["de"]=pd.to_numeric(out["borrowings"],errors="coerce")/(pd.to_numeric(out["equity_capital"],errors="coerce")+pd.to_numeric(out["reserves"],errors="coerce")).replace(0,np.nan)
    out["fcf"]=pd.to_numeric(out["operating_activity"],errors="coerce")+pd.to_numeric(out["investing_activity"],errors="coerce")
    out["icr"]=pd.to_numeric(out["operating_profit"],errors="coerce")/pd.to_numeric(out["interest"],errors="coerce").replace(0,np.nan)
    out["asset_turnover"]=out["sales"]/pd.to_numeric(out["total_assets"],errors="coerce").replace(0,np.nan)
    out["dividend_payout"]=pd.to_numeric(out["dividend_payout"],errors="coerce")

    for src,target,yrs in [("sales","revenue",5),("sales","revenue",3),("net_profit","pat",5),("eps","eps",5)]:
        if src in pnl:
            cg=_cagr(pnl,src,yrs).rename(columns={f"{src}_cagr_{yrs}yr":f"{target}_cagr_{yrs}yr"})
            out=out.merge(cg,on="company_id",how="left",suffixes=("","_calc"))
    for col in ["revenue_cagr_5yr","pat_cagr_5yr","eps_cagr_5yr","revenue_cagr_3yr"]:
        calc=col+"_calc"
        if calc in out: out[col]=pd.to_numeric(out.get(col),errors="coerce").fillna(pd.to_numeric(out[calc],errors="coerce"))
    if not mc.empty: out=out.merge(mc,on="company_id",how="left")
    for col in ["pe_ratio","pb_ratio","dividend_yield_pct","market_cap"]:
        if col not in out: out[col]=np.nan
    return out.drop_duplicates("company_id").reset_index(drop=True), pnl, bs

def _winsor(s):
    x=pd.to_numeric(s,errors="coerce")
    if x.notna().sum()<2: return pd.Series(50.,index=s.index)
    lo,hi=x.quantile(.10),x.quantile(.90)
    if pd.isna(lo) or pd.isna(hi) or hi==lo: return pd.Series(50.,index=s.index)
    return ((x.clip(lo,hi)-lo)/(hi-lo)*100).fillna(50)

def add_composite_score(df):
    x=df.copy()
    for c in ["roe","roce","npm","fcf","revenue_cagr_5yr","pat_cagr_5yr","de","icr"]:
        if c not in x: x[c]=np.nan
    x["profitability_score"]=.15*_winsor(x.roe)+.10*_winsor(x.roce)+.10*_winsor(x.npm)
    fcf_cagr = x.get("fcf_cagr_5yr", pd.Series(np.nan, index=x.index))
    cfo_pat = x.get("cfo_pat", pd.Series(np.nan, index=x.index))
    x["cash_quality_score"] = (
        .15 * _winsor(fcf_cagr)
        + .10 * _winsor(cfo_pat)
        + .05 * _winsor((x.fcf > 0).astype(float))
    )
    x["growth_score"]=.10*_winsor(x.revenue_cagr_5yr)+.10*_winsor(x.pat_cagr_5yr)
    de_score = 100 - _winsor(x.de)
    x["leverage_score"] = .10 * de_score + .05 * _winsor(x.icr)
    x["composite_quality_score"]=(x["profitability_score"]+x["cash_quality_score"]+x["growth_score"]+x["leverage_score"]).clip(0,100)
    # Unit tests and standalone callers may not provide broad_sector.
    # In that case, calculate the sector-relative score against the full
    # supplied universe instead of failing on a missing column.
    if "broad_sector" in x.columns:
        x["sector_relative_score"] = (
            x.groupby("broad_sector", dropna=False)["composite_quality_score"]
             .transform(_winsor)
        )
    else:
        x["sector_relative_score"] = _winsor(x["composite_quality_score"])
    return x.sort_values("composite_quality_score",ascending=False)

def apply_filters(df, thresholds):
    """
    Apply Sprint-3 preset filters.

    The preset YAML uses business-friendly names (for example
    free_cash_flow_min and pe_max), while the dataframe uses the
    normalized metric names below. Missing metrics are treated as
    unavailable rather than being used as a scalar boolean index.
    """
    x = df.copy()

    aliases = {
        "roe": "roe",
        "roce": "roce",
        "free_cash_flow": "fcf",
        "fcf": "fcf",
        "revenue_cagr_5yr": "revenue_cagr_5yr",
        "revenue_cagr_3yr": "revenue_cagr_3yr",
        "pat_cagr_5yr": "pat_cagr_5yr",
        "eps_cagr": "eps_cagr_5yr",
        "opm": "opm",
        "pe": "pe_ratio",
        "pb": "pb_ratio",
        "dividend_yield": "dividend_yield_pct",
        "dividend_payout": "dividend_payout",
        "icr": "icr",
        "market_cap": "market_cap",
        "net_profit": "net_profit",
        "asset_turnover": "asset_turnover",
        "sales": "sales",
        "de": "de",
    }

    def metric_series(key):
        col = aliases.get(key, key)
        if col in x.columns:
            return pd.to_numeric(x[col], errors="coerce")
        return pd.Series(np.nan, index=x.index, dtype="float64")

    for key, t in thresholds.items():
        if key == "debt_declining_yoy":
            continue

        if key == "debt_to_equity_max":
            fin = x["broad_sector"].astype(str).str.lower().str.contains(
                "financial|bank|nbfc|insurance", regex=True, na=False
            )
            x = x[fin | (metric_series("de") < float(t))]
            continue

        if key.endswith("_min"):
            metric = key[:-4]
            # Public `min` filters use inclusive >= semantics.
            x = x[metric_series(metric) >= float(t)]

        elif key.endswith("_max"):
            metric = key[:-4]
            # Public `max` filters use inclusive <= semantics.
            x = x[metric_series(metric) <= float(t)]

    if thresholds.get("debt_declining_yoy"):
        # If history is available in the dataframe, compare the two
        # latest D/E observations. For the latest-only universe, use
        # the precomputed flag when present.
        if "debt_declining_yoy" in x.columns:
            x = x[x["debt_declining_yoy"].fillna(False).astype(bool)]
        else:
            ids = set()
            history = df.copy()
            needed = {"company_id", "borrowings", "equity_capital", "reserves", "year"}
            if needed.issubset(history.columns):
                b = history[list(needed)].copy()
                b["year_num"] = b["year"].map(_year)
                denom = (
                    pd.to_numeric(b["equity_capital"], errors="coerce")
                    + pd.to_numeric(b["reserves"], errors="coerce")
                ).replace(0, np.nan)
                b["de"] = pd.to_numeric(
                    b["borrowings"], errors="coerce"
                ) / denom

                for cid, g in (
                    b.dropna(subset=["year_num"])
                     .sort_values("year_num")
                     .groupby("company_id")
                ):
                    if len(g) >= 2:
                        latest = g.iloc[-1]["de"]
                        prior = g.iloc[-2]["de"]
                        if pd.notna(latest) and pd.notna(prior) and latest < prior:
                            ids.add(cid)
            x = x[x.company_id.isin(ids)]

    return x

def run_preset(name, db_path=DB):
    cfg=load_config()
    if name not in cfg["presets"]: raise KeyError(name)
    df,_,_=load_universe(db_path)
    return apply_filters(add_composite_score(df),cfg["presets"][name])

def run_all(db_path=DB):
    cfg=load_config()
    df,_,_=load_universe(db_path)
    base=add_composite_score(df)
    return {n:apply_filters(base,rules) for n,rules in cfg["presets"].items()}

if __name__=="__main__":
    for n,d in run_all().items(): print(f"{n}: {len(d)} companies")
