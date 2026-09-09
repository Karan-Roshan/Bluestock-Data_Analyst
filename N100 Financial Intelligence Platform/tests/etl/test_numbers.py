from src.etl.normaliser import normalize_number, clean_column_name


def test_number_integer():
    assert normalize_number(100) == 100.0


def test_number_comma():
    assert normalize_number("1,234.50") == 1234.5


def test_number_percent():
    assert normalize_number("25%") == 0.25


def test_number_dash():
    assert normalize_number("-") is None


def test_clean_columns():
    assert clean_column_name("Operating Profit %") == "operating_profit"
