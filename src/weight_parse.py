"""Parse weight string (from scraper weight_unit / name) into numeric weight + measure code."""

import re
from typing import Optional, Tuple

# Normalize Cyrillic / Latin unit tokens to API-friendly codes (weightMeasure)
_UNIT_MAP = {
    "кг": "kg",
    "kg": "kg",
    "г": "g",
    "г.": "g",
    "гр": "g",
    "g": "g",
    "л": "L",
    "l": "L",
    "мл": "ml",
    "ml": "ml",
    "бр": "pcs",
    "бр.": "pcs",
}


def parse_weight_and_measure(text: Optional[str]) -> Tuple[Optional[float], Optional[str]]:
    """
    Extract first quantity + unit from strings like '330 мл', '1,5 л', '500 г', '2 бр.'.
    Returns (None, None) if nothing matches.
    """
    if not text or not str(text).strip():
        return None, None
    s = str(text).strip()
    pattern = re.compile(
        r"(\d+[.,]?\d*)\s*(кг|г\.?|гр|мл|л\.?|ml|ML|kg|KG|g|G|l|L|бр\.?)\b",
        re.IGNORECASE,
    )
    m = pattern.search(s.replace(" ", " "))
    if not m:
        return None, None
    raw_num, raw_unit = m.group(1), m.group(2)
    try:
        num = float(raw_num.replace(",", "."))
    except ValueError:
        return None, None
    key = raw_unit.lower().rstrip(".")
    if key == "гр":
        key = "г"
    measure = _UNIT_MAP.get(key) or _UNIT_MAP.get(raw_unit.lower()) or raw_unit.strip()
    return num, measure
