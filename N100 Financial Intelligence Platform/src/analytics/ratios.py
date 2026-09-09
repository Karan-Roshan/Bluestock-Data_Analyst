"""Profitability, leverage and efficiency ratios."""


def net_profit_margin(net_profit, sales):
    if sales in (None, 0):
        return None
    return net_profit / sales * 100


def operating_profit_margin(operating_profit, sales):
    if sales in (None, 0):
        return None
    return operating_profit / sales * 100


def opm_cross_check(computed, source):
    if computed is None or source is None:
        return None
    return abs(computed - source) > 1.0


def return_on_equity(net_profit, equity_capital, reserves):
    denominator = (equity_capital or 0) + (reserves or 0)
    if denominator <= 0:
        return None
    return net_profit / denominator * 100


def return_on_capital_employed(ebit, equity_capital, reserves, borrowings):
    denominator = (equity_capital or 0) + (reserves or 0) + (borrowings or 0)
    if denominator <= 0:
        return None
    return ebit / denominator * 100


def return_on_assets(net_profit, total_assets):
    if total_assets in (None, 0):
        return None
    return net_profit / total_assets * 100


def debt_to_equity(borrowings, equity_capital, reserves):
    if borrowings == 0:
        return 0
    denominator = (equity_capital or 0) + (reserves or 0)
    if denominator <= 0:
        return None
    return borrowings / denominator


def high_leverage_flag(de, broad_sector):
    if de is None:
        return False
    if broad_sector == "Financials":
        return False
    return de > 5


def interest_coverage(operating_profit, other_income, interest):
    if interest in (None, 0):
        return None
    return (operating_profit + (other_income or 0)) / interest


def icr_label(icr):
    return "Debt Free" if icr is None else "Covered"


def icr_warning(icr):
    return icr is not None and icr < 1.5


def net_debt(borrowings, investments):
    if borrowings is None or investments is None:
        return None
    return borrowings - investments


def asset_turnover(sales, total_assets):
    if total_assets in (None, 0):
        return None
    return sales / total_assets


def book_value_per_share(equity_capital, reserves, shares=10):
    if shares in (None, 0):
        return None
    return ((equity_capital or 0) + (reserves or 0)) / shares


def dividend_payout_ratio(dividend, net_profit):
    if net_profit in (None, 0):
        return None
    return dividend / net_profit * 100


def composite_quality_score(roe, roa, de, icr):
    """Simple 0-100 score, intentionally transparent rather than magical."""
    score = 0

    if roe is not None and roe > 15:
        score += 30
    if roa is not None and roa > 8:
        score += 20
    if de is not None and de < 1:
        score += 20
    if icr is None or icr >= 1.5:
        score += 15
    if icr is not None and icr >= 3:
        score += 15

    return score
