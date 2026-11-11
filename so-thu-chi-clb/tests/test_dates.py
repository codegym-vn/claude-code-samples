from datetime import date

import pytest

from app.dates import format_date_vn, month_range, next_month, parse_month, previous_month


def test_month_range_handles_leap_february():
    assert month_range(2028, 2) == (date(2028, 2, 1), date(2028, 2, 29))
    assert month_range(2026, 2) == (date(2026, 2, 1), date(2026, 2, 28))


def test_month_range_thirty_one_days():
    first, last = month_range(2026, 10)
    assert first == date(2026, 10, 1)
    assert last == date(2026, 10, 31)


@pytest.mark.parametrize("text", ["2026-13", "2026", "abc", "2026-00"])
def test_parse_month_rejects_invalid(text):
    with pytest.raises(ValueError):
        parse_month(text)


def test_previous_and_next_month_wrap_year():
    assert previous_month(2026, 1) == (2025, 12)
    assert next_month(2026, 12) == (2027, 1)
    assert next_month(2026, 5) == (2026, 6)


def test_format_date_vn():
    assert format_date_vn("2026-03-09") == "09/03/2026"
    assert format_date_vn(None) == ""
