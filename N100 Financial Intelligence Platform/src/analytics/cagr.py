"""Simple CAGR functions with all six required edge cases."""


def cagr(start, end, years):
    """
    Return (value, flag).

    Flags:
    - None: normal calculation
    - DECLINE_TO_LOSS
    - TURNAROUND
    - BOTH_NEGATIVE
    - ZERO_BASE
    - INSUFFICIENT
    """
    if years is None or years <= 0:
        return None, "INSUFFICIENT"

    if start is None or end is None:
        return None, "INSUFFICIENT"

    if start == 0:
        return None, "ZERO_BASE"

    if start > 0 and end > 0:
        value = ((end / start) ** (1 / years) - 1) * 100
        return value, None

    if start > 0 and end < 0:
        return None, "DECLINE_TO_LOSS"

    if start < 0 and end > 0:
        return None, "TURNAROUND"

    if start < 0 and end < 0:
        return None, "BOTH_NEGATIVE"

    return None, "INSUFFICIENT"


def growth_for_window(history, current_year, column, years):
    """Find the value N years before current_year and calculate CAGR."""
    target_year = current_year - years
    start_row = history.get(target_year)
    end_row = history.get(current_year)

    if start_row is None or end_row is None:
        return None, "INSUFFICIENT"

    return cagr(start_row.get(column), end_row.get(column), years)
