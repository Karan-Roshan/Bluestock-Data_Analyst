"""Run the complete Sprint 2 ratio engine.""" 

import csv
import os
import sqlite3
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

from ratios import (
    net_profit_margin, operating_profit_margin, opm_cross_check,
    return_on_equity, return_on_capital_employed, return_on_assets,
    debt_to_equity, high_leverage_flag, interest_coverage, icr_label,
    icr_warning, net_debt, asset_turnover, book_value_per_share,
    dividend_payout_ratio, composite_quality_score,
)
from cagr import growth_for_window
from cashflow_kpis import (
    free_cash_flow, cfo_quality_score, cfo_quality_label,
    capex_intensity, capex_label, fcf_conversion_rate,
    capital_allocation_pattern, sign,
)

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "nifty100.db")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
OUTPUT_DIR.mkdir(exist_ok=True)

BASE = Path(__file__).resolve().parents[2]
RAW = BASE / os.getenv("RAW_DATA_DIR", "data/raw")
SCHEMA = BASE / "db/schema.sql"


def build_database():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA.read_text(encoding="utf-8"))

    companies = pd.read_excel(RAW / "companies.xlsx")
    pnl = pd.read_excel(RAW / "profitandloss.xlsx")
    bs = pd.read_excel(RAW / "balancesheet.xlsx")
    cf = pd.read_excel(RAW / "cashflow.xlsx")

    # Keep simple source tables inside the same SQLite database so the extra
    # KPI calculations can be audited with SQL.
    companies.to_sql(
        "companies",
        con,
        if_exists="append",
        index=False
    )

    pnl.to_sql(
        "profitandloss",
        con,
        if_exists="append",
        index=False
    )

    bs.to_sql(
        "balancesheet",
        con,
        if_exists="append",
        index=False
    )

    cf.to_sql(
        "cashflow",
        con,
        if_exists="append",
        index=False
    )

    pnl_map = {(int(r.company_id), int(r.year)): r.to_dict() for _, r in pnl.iterrows()}
    bs_map = {(int(r.company_id), int(r.year)): r.to_dict() for _, r in bs.iterrows()}
    cf_map = {(int(r.company_id), int(r.year)): r.to_dict() for _, r in cf.iterrows()}

    # History indexed by company and year for CAGR.
    history = {}
    for cid in companies.company_id.astype(int):
        history[cid] = {}
        for year in sorted(set(pnl[pnl.company_id == cid].year.astype(int))):
            p = pnl_map[(cid, year)]
            history[cid][year] = {
                "sales": p["sales"],
                "net_profit": p["net_profit"],
                "eps": p["eps"],
            }

    output_rows = []
    capital_rows = []
    edge_lines = []

    for _, company in companies.iterrows():
        cid = int(company.company_id)
        sector = str(company.broad_sector)

        for year in sorted(history[cid]):
            p = pnl_map[(cid, year)]
            b = bs_map[(cid, year)]
            c = cf_map[(cid, year)]

            npm = net_profit_margin(p["net_profit"], p["sales"])
            opm = operating_profit_margin(p["operating_profit"], p["sales"])

            if opm_cross_check(opm, p["opm_percentage"]):
                edge_lines.append(
                    f"DQ-RATIO OPM | company={cid} year={year} | "
                    f"computed={opm:.4f} source={p['opm_percentage']:.4f} | "
                    f"category=version_difference"
                )

            roe = return_on_equity(
                p["net_profit"], b["equity_capital"], b["reserves"]
            )
            roce = return_on_capital_employed(
                p["operating_profit"], b["equity_capital"],
                b["reserves"], b["borrowings"]
            )
            roa = return_on_assets(p["net_profit"], b["total_assets"])

            de = debt_to_equity(
                b["borrowings"], b["equity_capital"], b["reserves"]
            )
            leverage = high_leverage_flag(de, sector)

            icr = interest_coverage(
                p["operating_profit"], p["other_income"], p["interest"]
            )
            label = icr_label(icr)
            warning = icr_warning(icr)

            nd = net_debt(b["borrowings"], b["investments"])
            turnover = asset_turnover(p["sales"], b["total_assets"])

            fcf = free_cash_flow(c["operating_activity"], c["investing_activity"])
            qscore = cfo_quality_score(c["operating_activity"], p["net_profit"])
            qlabel = cfo_quality_label(qscore)
            capex = abs(c["investing_activity"])
            intensity = capex_intensity(c["investing_activity"], p["sales"])
            intensity_label = capex_label(intensity)
            conversion = fcf_conversion_rate(fcf, p["operating_profit"])

            # 3/5/10-year CAGR.
            cagr_values = {}
            for metric, source_col in [
                ("revenue", "sales"), ("pat", "net_profit"), ("eps", "eps")
            ]:
                for window in [3, 5, 10]:
                    value, flag = growth_for_window(
                        history[cid], year, source_col, window
                    )
                    cagr_values[f"{metric}_cagr_{window}yr"] = value
                    cagr_values[f"{metric}_cagr_{window}yr_flag"] = flag

            bvps = book_value_per_share(
                b["equity_capital"], b["reserves"]
            )
            payout = dividend_payout_ratio(p["dividend"], p["net_profit"])
            score = composite_quality_score(roe, roa, de, icr)

            output_rows.append((
                cid, year, npm, opm, roe, roce, roa,
                de, int(leverage), icr, label, int(warning), nd, turnover,
                fcf, qscore, qlabel, capex, intensity, intensity_label,
                conversion, p["eps"], bvps, payout, b["borrowings"],
                c["operating_activity"],
                cagr_values["revenue_cagr_3yr"], cagr_values["revenue_cagr_3yr_flag"],
                cagr_values["revenue_cagr_5yr"], cagr_values["revenue_cagr_5yr_flag"],
                cagr_values["revenue_cagr_10yr"], cagr_values["revenue_cagr_10yr_flag"],
                cagr_values["pat_cagr_3yr"], cagr_values["pat_cagr_3yr_flag"],
                cagr_values["pat_cagr_5yr"], cagr_values["pat_cagr_5yr_flag"],
                cagr_values["pat_cagr_10yr"], cagr_values["pat_cagr_10yr_flag"],
                cagr_values["eps_cagr_3yr"], cagr_values["eps_cagr_3yr_flag"],
                cagr_values["eps_cagr_5yr"], cagr_values["eps_cagr_5yr_flag"],
                cagr_values["eps_cagr_10yr"], cagr_values["eps_cagr_10yr_flag"],
                score
            ))

            capital_rows.append({
                "company_id": cid,
                "year": year,
                "cfo_sign": sign(c["operating_activity"]),
                "cfi_sign": sign(c["investing_activity"]),
                "cff_sign": sign(c["financing_activity"]),
                "pattern_label": capital_allocation_pattern(
                    c["operating_activity"], c["investing_activity"],
                    c["financing_activity"], qscore
                ),
            })

            # Source cross-checks are most useful on the latest available year.
            if year == max(history[cid]):
                source_roe = company.roe_percentage
                source_roce = company.roce_percentage

                if pd.notna(source_roe) and roe is not None and abs(roe - source_roe) > 5:
                    edge_lines.append(
                        f"ROE | company={cid} year={year} | computed={roe:.4f} "
                        f"source={source_roe:.4f} | category=data_source_issue"
                    )

                if pd.notna(source_roce) and roce is not None and abs(roce - source_roce) > 5:
                    edge_lines.append(
                        f"ROCE | company={cid} year={year} | computed={roce:.4f} "
                        f"source={source_roce:.4f} | category=data_source_issue"
                    )

    sql = """
    INSERT INTO financial_ratios (
        company_id, year,
        net_profit_margin_pct, operating_profit_margin_pct, return_on_equity_pct,
        roce_pct, return_on_assets_pct, debt_to_equity, high_leverage_flag,
        interest_coverage, icr_label, icr_warning_flag, net_debt_cr, asset_turnover,
        free_cash_flow_cr, cfo_quality_score, cfo_quality_label, capex_cr,
        capex_intensity_pct, capex_intensity_label, fcf_conversion_rate_pct,
        earnings_per_share, book_value_per_share, dividend_payout_ratio_pct,
        total_debt_cr, cash_from_operations_cr,
        revenue_cagr_3yr, revenue_cagr_3yr_flag,
        revenue_cagr_5yr, revenue_cagr_5yr_flag,
        revenue_cagr_10yr, revenue_cagr_10yr_flag,
        pat_cagr_3yr, pat_cagr_3yr_flag,
        pat_cagr_5yr, pat_cagr_5yr_flag,
        pat_cagr_10yr, pat_cagr_10yr_flag,
        eps_cagr_3yr, eps_cagr_3yr_flag,
        eps_cagr_5yr, eps_cagr_5yr_flag,
        eps_cagr_10yr, eps_cagr_10yr_flag,
        composite_quality_score
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """

    con.executemany(sql, output_rows)

    # Add extra transparent KPIs from the source tables.
    con.execute("""
        UPDATE financial_ratios
        SET
            ebit_margin_pct = operating_profit_margin_pct,
            tax_rate_pct = CASE
                WHEN company_id IS NOT NULL THEN (
                    SELECT CASE WHEN p.profit_before_tax IS NULL OR p.profit_before_tax = 0
                                THEN NULL
                                ELSE p.tax / p.profit_before_tax * 100 END
                    FROM profitandloss p
                    WHERE p.company_id = financial_ratios.company_id AND p.year = financial_ratios.year
                ) END,
            expense_to_sales_pct = (
                SELECT CASE WHEN p.sales IS NULL OR p.sales = 0 THEN NULL
                            ELSE p.expenses / p.sales * 100 END
                FROM profitandloss p
                WHERE p.company_id = financial_ratios.company_id AND p.year = financial_ratios.year
            ),
            cfo_margin_pct = CASE WHEN cash_from_operations_cr IS NULL THEN NULL
                                  ELSE cash_from_operations_cr * 100.0 /
                                       (SELECT p.sales FROM profitandloss p
                                        WHERE p.company_id = financial_ratios.company_id AND p.year = financial_ratios.year) END,
            fcf_margin_pct = CASE WHEN free_cash_flow_cr IS NULL THEN NULL
                                  ELSE free_cash_flow_cr * 100.0 /
                                       (SELECT p.sales FROM profitandloss p
                                        WHERE p.company_id = financial_ratios.company_id AND p.year = financial_ratios.year) END,
            net_debt_to_equity = CASE WHEN return_on_equity_pct IS NULL THEN NULL
                                      ELSE net_debt_cr / NULLIF((SELECT b.equity_capital + b.reserves
                                                                  FROM balancesheet b
                                                                  WHERE b.company_id = financial_ratios.company_id AND b.year = financial_ratios.year), 0) END,
            cash_to_debt_pct = 100.0 *
                (SELECT b.cash FROM balancesheet b WHERE b.company_id = financial_ratios.company_id AND b.year = financial_ratios.year)
                / NULLIF(total_debt_cr, 0),
            investments_to_debt_pct = 100.0 *
                (SELECT b.investments FROM balancesheet b WHERE b.company_id = financial_ratios.company_id AND b.year = financial_ratios.year)
                / NULLIF(total_debt_cr, 0)
    """)

    # YoY growth metrics use the immediately previous year.
    con.execute("""
        UPDATE financial_ratios AS f
        SET revenue_growth_yoy_pct = (
            SELECT CASE WHEN p0.sales = 0 THEN NULL ELSE (p1.sales / p0.sales - 1) * 100 END
            FROM profitandloss p0
            JOIN profitandloss p1 ON p1.company_id = p0.company_id AND p1.year = p0.year - 1
            WHERE p0.company_id = f.company_id AND p0.year = f.year
        ),
        pat_growth_yoy_pct = (
            SELECT CASE WHEN p0.net_profit = 0 THEN NULL ELSE (p1.net_profit / p0.net_profit - 1) * 100 END
            FROM profitandloss p0
            JOIN profitandloss p1 ON p1.company_id = p0.company_id AND p1.year = p0.year - 1
            WHERE p0.company_id = f.company_id AND p0.year = f.year
        ),
        eps_growth_yoy_pct = (
            SELECT CASE WHEN p0.eps = 0 THEN NULL ELSE (p1.eps / p0.eps - 1) * 100 END
            FROM profitandloss p0
            JOIN profitandloss p1 ON p1.company_id = p0.company_id AND p1.year = p0.year - 1
            WHERE p0.company_id = f.company_id AND p0.year = f.year
        ),
        operating_profit_growth_yoy_pct = (
            SELECT CASE WHEN p0.operating_profit = 0 THEN NULL ELSE (p1.operating_profit / p0.operating_profit - 1) * 100 END
            FROM profitandloss p0
            JOIN profitandloss p1 ON p1.company_id = p0.company_id AND p1.year = p0.year - 1
            WHERE p0.company_id = f.company_id AND p0.year = f.year
        )
    """)

    con.commit()

    with (OUTPUT_DIR / "capital_allocation.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "company_id", "year", "cfo_sign", "cfi_sign", "cff_sign", "pattern_label"
        ])
        writer.writeheader()
        writer.writerows(capital_rows)

    with (OUTPUT_DIR / "ratio_edge_cases.log").open("w", encoding="utf-8") as f:
        f.write("SPRINT 2 RATIO EDGE CASE LOG\n")
        f.write("Categories: data_source_issue, version_difference, formula_discrepancy\n\n")
        if edge_lines:
            f.write("\n".join(edge_lines))
            f.write("\n")
        else:
            f.write("No anomalies found.\n")

    count = con.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]
    con.close()

    print(f"financial_ratios rows: {count}")
    print(f"capital allocation: {OUTPUT_DIR / 'capital_allocation.csv'}")
    print(f"edge-case log: {OUTPUT_DIR / 'ratio_edge_cases.log'}")

    if count < 1100:
        raise SystemExit("FAIL: financial_ratios has fewer than 1,100 rows")


if __name__ == "__main__":
    build_database()
