"""Date helpers. Dates are stored in the database as ISO strings (YYYY-MM-DD)."""

import calendar
from datetime import date


def today() -> date:
    """Return today's date. Kept as a function so tests can replace it."""
    return date.today()


def parse_iso_date(text: str) -> date:
    """Parse "YYYY-MM-DD"; raise ValueError with a Vietnamese message if invalid."""
    try:
        return date.fromisoformat(text.strip())
    except ValueError as exc:
        raise ValueError("Ngày không hợp lệ, dùng định dạng YYYY-MM-DD.") from exc


def parse_month(text: str) -> tuple[int, int]:
    """Parse a month key "YYYY-MM" into (year, month)."""
    try:
        year_part, month_part = text.strip().split("-")
        year, month = int(year_part), int(month_part)
    except ValueError as exc:
        raise ValueError("Tháng không hợp lệ, dùng định dạng YYYY-MM.") from exc
    if not 1 <= month <= 12:
        raise ValueError("Tháng phải nằm trong khoảng 1 đến 12.")
    return year, month


def month_key(year: int, month: int) -> str:
    """Build the "YYYY-MM" key used for dues months."""
    return f"{year:04d}-{month:02d}"


def current_month_key() -> str:
    d = today()
    return month_key(d.year, d.month)


def month_range(year: int, month: int) -> tuple[date, date]:
    """Return the first and the last day of a month."""
    last = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last)


def previous_month(year: int, month: int) -> tuple[int, int]:
    if month == 1:
        return year - 1, 12
    return year, month - 1


def next_month(year: int, month: int) -> tuple[int, int]:
    if month == 12:
        return year + 1, 1
    return year, month + 1


def format_date_vn(iso_text: str | None) -> str:
    """Show an ISO date as dd/mm/yyyy; empty string for missing values."""
    if not iso_text:
        return ""
    d = date.fromisoformat(iso_text)
    return d.strftime("%d/%m/%Y")
