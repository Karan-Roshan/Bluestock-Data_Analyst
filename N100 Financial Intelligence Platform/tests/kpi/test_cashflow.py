from src.analytics.cashflow_kpis import (
    free_cash_flow, cfo_quality_score, cfo_quality_label,
    capex_intensity, capex_label, fcf_conversion_rate,
    capital_allocation_pattern
)


def test_fcf_can_be_negative():
    assert free_cash_flow(100, -150) == -50


def test_cfo_quality_zero_pat():
    assert cfo_quality_score(100, 0) is None


def test_cfo_quality_high():
    assert cfo_quality_label(1.2) == "High Quality"


def test_cfo_quality_moderate():
    assert cfo_quality_label(0.7) == "Moderate"


def test_cfo_quality_risk():
    assert cfo_quality_label(0.3) == "Accrual Risk"


def test_capex_asset_light():
    assert capex_label(2) == "Asset Light"


def test_capex_moderate():
    assert capex_label(5) == "Moderate"


def test_capex_intensive():
    assert capex_label(10) == "Capital Intensive"


def test_fcf_conversion_zero_op():
    assert fcf_conversion_rate(100, 0) is None


def test_pattern_reinvestor():
    assert capital_allocation_pattern(100, -50, -20, 0.8) == "Reinvestor"


def test_pattern_shareholder_returns():
    assert capital_allocation_pattern(120, -50, -20, 1.2) == "Shareholder Returns"


def test_pattern_distress():
    assert capital_allocation_pattern(-100, 50, 40, 0.5) == "Distress Signal"


def test_pattern_debt_growth():
    assert capital_allocation_pattern(-100, -50, 40, 0.5) == "Growth Funded by Debt"
