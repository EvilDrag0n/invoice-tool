import re
from decimal import Decimal, InvalidOperation


WHITESPACE_RE = re.compile(r"\s+")


def collapse_whitespace(value: str) -> str:
    return WHITESPACE_RE.sub(" ", value).strip()


def normalize_date(value: str) -> str:
    cleaned = collapse_whitespace(value)
    match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", cleaned)
    if not match:
        raise ValueError(f"Unsupported date format: {value}")
    year, month, day = match.groups()
    return f"{year}-{int(month):02d}-{int(day):02d}"


def normalize_decimal(value: str) -> str:
    cleaned = collapse_whitespace(value)
    cleaned = cleaned.replace("¥", "").replace(",", "")
    cleaned = cleaned.replace("（小写）", "").replace("(小写)", "")
    cleaned = cleaned.strip()
    if not cleaned:
        raise ValueError("Decimal value is empty")
    try:
        decimal_value = Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid decimal value: {value}") from exc
    return format(decimal_value.quantize(Decimal("0.01")), "f")
