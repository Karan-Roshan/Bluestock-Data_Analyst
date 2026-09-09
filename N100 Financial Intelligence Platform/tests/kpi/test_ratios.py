from src.analytics.ratios import (
    net_profit_margin, operating_profit_margin, opm_cross_check,
    return_on_equity, return_on_capital_employed, return_on_assets,
    debt_to_equity, high_leverage_flag, interest_coverage, icr_label,
    icr_warning, net_debt, asset_turnover, dividend_payout_ratio
)


def test_npm_normal():
    assert net_profit_margin(20, 100) == 20


def test_npm_zero_sales():
    assert net_profit_margin(20, 0) is None


def test_opm_normal():
    assert operating_profit_margin(30, 100) == 30


def test_opm_zero_sales():
    assert operating_profit_margin(30, 0) is None


def test_opm_cross_check_mismatch():
    assert opm_cross_check(20, 25) is True


def test_opm_cross_check_match():
    assert opm_cross_check(20, 20.5) is False


def test_roe_normal():
    assert return_on_equity(20, 50, 50) == 20


def test_roe_negative_equity():
    assert return_on_equity(20, 50, -60) is None


def test_roce_normal():
    assert return_on_capital_employed(30, 50, 50, 50) == 20


def test_roa_normal():
    assert return_on_assets(20, 100) == 20


def test_roa_zero_assets():
    assert return_on_assets(20, 0) is None


def test_debt_free_is_zero():
    assert debt_to_equity(0, 100, 100) == 0


def test_de_normal():
    assert debt_to_equity(50, 100, 100) == 0.25


def test_high_debt_flag():
    assert high_leverage_flag(6, "Consumer") is True


def test_financials_high_debt_suppressed():
    assert high_leverage_flag(6, "Financials") is False


def test_icr_zero_interest():
    assert interest_coverage(30, 5, 0) is None


def test_icr_label_debt_free():
    assert icr_label(None) == "Debt Free"


def test_icr_warning():
    assert icr_warning(1.2) is True


def test_net_debt():
    assert net_debt(100, 30) == 70


def test_asset_turnover_zero_assets():
    assert asset_turnover(100, 0) is None


def test_payout():
    assert dividend_payout_ratio(10, 100) == 10
