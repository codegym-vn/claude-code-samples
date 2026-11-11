import pytest

from app.money import format_vnd, parse_vnd, round_vnd


@pytest.mark.parametrize(
    "text, expected",
    [
        ("50000", 50_000),
        ("50.000", 50_000),
        (" 1.250.000 ", 1_250_000),
        ("75 000", 75_000),
        ("120.000đ", 120_000),
    ],
)
def test_parse_vnd_accepts_common_formats(text, expected):
    assert parse_vnd(text) == expected


@pytest.mark.parametrize("text", ["", "abc", "50,5", "50.5", "-20000", "0", "12.34.567"])
def test_parse_vnd_rejects_invalid_amounts(text):
    with pytest.raises(ValueError):
        parse_vnd(text)


def test_parse_vnd_returns_int():
    assert isinstance(parse_vnd("50.000"), int)


def test_format_vnd_uses_dot_separator():
    assert format_vnd(1_234_567) == "1.234.567 đ"
    assert format_vnd(0) == "0 đ"
    assert format_vnd(-50_000) == "-50.000 đ"


def test_round_vnd():
    assert round_vnd(12_345) == 12_000
    assert round_vnd(250_000) == 250_000
