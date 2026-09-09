"""Small, readable normalisation helpers."""

import math
import re
from typing import Any


def normalize_year(value: Any):
    """Convert common year values such as 2024, 'FY24', '2023-24' to an integer."""
    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    text = str(value).strip().upper()
    if not text:
        return None

    match = re.search(r"(20\d{2}|19\d{2})", text)
    if match:
        return int(match.group(1))

    match = re.search(r"\bFY\s*['-]?(\d{2})\b", text)
    if match:
        yy = int(match.group(1))
        return 2000 + yy if yy < 50 else 1900 + yy

    return None


def normalize_ticker(value: Any):
    """Return a clean uppercase ticker without exchange prefixes."""
    if value is None:
        return None

    text = str(value).strip().upper()
    if not text:
        return None

    text = text.replace("NSE:", "").replace("BSE:", "")
    text = re.sub(r"\s+", "", text)
    return text


def clean_column_name(value: Any):
    """Make Excel column names easy to match."""
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def normalize_number(value: Any):
    """Convert commas, percent signs and '-' to numbers where possible."""
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)

    text = str(value).strip().replace(",", "")
    if text in {"", "-", "--", "nan", "none"}:
        return None

    percent = text.endswith("%")
    if percent:
        text = text[:-1]

    try:
        number = float(text)
        return number / 100 if percent else number
    except ValueError:
        return None
