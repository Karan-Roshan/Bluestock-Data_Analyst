import re
import math


def normalize_ticker(value):
    """Normalize ticker symbols."""
    if value is None:
        return None

    value = str(value).strip().upper()

    if not value:
        return None

    # NSE:TCS -> TCS
    # BSE:500325 -> 500325
    if ":" in value:
        value = value.split(":")[-1]

    return value.strip()


def normalize_year(value):
    """Normalize financial-year values to YYYY."""
    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    value = str(value).strip().upper()

    if not value:
        return None

    # FY24 -> 2024
    # FY 24 -> 2024
    match = re.fullmatch(r"FY\s*[-]?\s*['\"]?(\d{2})", value)

    if match:
        return 2000 + int(match.group(1))

    # 2024 -> 2024
    match = re.search(r"\b(19\d{2}|20\d{2})\b", value)

    if match:
        return int(match.group(1))

    # 24 -> 2024
    match = re.fullmatch(r"(\d{2})", value)

    if match:
        return 2000 + int(match.group(1))

    # '24 should NOT be accepted
    return None


def normalize_number(value):
    """Normalize financial numbers into float."""
    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()

    if not value:
        return None

    # Percentage:
    # 25% -> 0.25
    if value.endswith("%"):
        try:
            number = value[:-1].replace(",", "").strip()
            return float(number) / 100
        except ValueError:
            return None

    # Remove commas and currency symbols
    value = value.replace(",", "")
    value = value.replace("₹", "")
    value = value.replace("$", "")
    value = value.strip()

    # Accounting format:
    # (123.45) -> -123.45
    if value.startswith("(") and value.endswith(")"):
        value = "-" + value[1:-1]

    try:
        return float(value)
    except ValueError:
        return None


def clean_column_name(value):
    """Convert column names to snake_case."""
    if value is None:
        return ""

    value = str(value).strip().lower()

    value = re.sub(r"[^a-z0-9]+", "_", value)

    return value.strip("_")

def clean_columns(df):
    """Clean all DataFrame column names."""
    df = df.copy()
    df.columns = [clean_column_name(col) for col in df.columns]
    return df


def clean_number(value):
    """Backward-compatible alias for normalize_number."""
    return normalize_number(value)


def clean_text(value):
    """Clean text values."""
    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    value = str(value).strip()

    return value if value else None


def find_column(df, candidates):
    """Find the first matching column from a list of candidates."""
    columns = {
        clean_column_name(col): col
        for col in df.columns
    }

    for candidate in candidates:
        cleaned = clean_column_name(candidate)

        if cleaned in columns:
            return columns[cleaned]

    return None


def add_period_year(df, period_column="period"):
    """Add a normalized year column from a period column."""
    df = df.copy()

    if period_column not in df.columns:
        return df

    df["year"] = df[period_column].apply(normalize_year)

    return df