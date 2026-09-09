from src.analytics.cagr import cagr, growth_for_window


def test_cagr_normal():
    value, flag = cagr(100, 121, 2)
    assert round(value, 2) == 10.0
    assert flag is None


def test_cagr_zero_base():
    assert cagr(0, 100, 5) == (None, "ZERO_BASE")


def test_cagr_turnaround():
    assert cagr(-100, 100, 5) == (None, "TURNAROUND")


def test_cagr_decline_to_loss():
    assert cagr(100, -100, 5) == (None, "DECLINE_TO_LOSS")


def test_cagr_both_negative():
    assert cagr(-100, -50, 5) == (None, "BOTH_NEGATIVE")


def test_cagr_insufficient():
    assert cagr(None, 100, 5) == (None, "INSUFFICIENT")


def test_growth_window():
    history = {
        2020: {"sales": 100},
        2025: {"sales": 150},
    }
    value, flag = growth_for_window(history, 2025, "sales", 5)
    assert round(value, 2) == round(((150/100)**(1/5)-1)*100, 2)
    assert flag is None
