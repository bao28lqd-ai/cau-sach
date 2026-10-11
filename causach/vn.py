"""Vietnamese number formatting: 5.110 for thousands, 22,8 for decimals, 22,8% for shares."""
from __future__ import annotations


def fmt_int(value) -> str:
    return f"{int(round(float(value))):,}".replace(",", ".")


def fmt_dec(value, digits: int = 1) -> str:
    whole, _, frac = f"{float(value):,.{digits}f}".partition(".")
    whole = whole.replace(",", ".")
    return f"{whole},{frac}" if digits else whole


def fmt_pct(share, digits: int = 0) -> str:
    return f"{fmt_dec(float(share) * 100, digits)}%"


def fmt_frac(part: int, whole: int) -> str:
    return f"{part}/{whole} ({fmt_pct(part / whole)})" if whole else "—"
