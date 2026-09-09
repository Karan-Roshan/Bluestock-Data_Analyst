"""Cash-flow KPI functions kept small so they are easy to test."""


def free_cash_flow(cfo, cfi):
    if cfo is None or cfi is None:
        return None
    return cfo + cfi


def cfo_quality_score(cfo, pat):
    if cfo is None or pat in (None, 0):
        return None
    return cfo / pat


def cfo_quality_label(score):
    if score is None:
        return None
    if score > 1.0:
        return "High Quality"
    if score >= 0.5:
        return "Moderate"
    return "Accrual Risk"


def capex_intensity(cfi, sales):
    if cfi is None or sales in (None, 0):
        return None
    return abs(cfi) / sales * 100


def capex_label(value):
    if value is None:
        return None
    if value < 3:
        return "Asset Light"
    if value <= 8:
        return "Moderate"
    return "Capital Intensive"


def fcf_conversion_rate(fcf, operating_profit):
    if fcf is None or operating_profit in (None, 0):
        return None
    return fcf / operating_profit * 100


def sign(value):
    if value is None or value == 0:
        return "0"
    return "+" if value > 0 else "-"


def capital_allocation_pattern(cfo, cfi, cff, cfo_pat_score=None):
    """
    Classify the sign combination.

    The (+,-,-) combination is split using CFO/PAT quality:
    high quality -> Shareholder Returns
    otherwise -> Reinvestor
    """
    key = (sign(cfo), sign(cfi), sign(cff))

    if key == ("+", "-", "-"):
        if cfo_pat_score is not None and cfo_pat_score > 1.0:
            return "Shareholder Returns"
        return "Reinvestor"

    labels = {
        ("+", "+", "-"): "Liquidating Assets",
        ("-", "+", "+"): "Distress Signal",
        ("-", "-", "+"): "Growth Funded by Debt",
        ("+", "+", "+"): "Cash Accumulator",
        ("-", "-", "-"): "Pre-Revenue",
        ("+", "-", "+"): "Mixed",
    }

    return labels.get(key, "Mixed")
