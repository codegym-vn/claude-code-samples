"""Money helpers.

All amounts in this application are integers in Vietnamese dong (VND).
"""


def parse_vnd(text: str) -> int:
    """Parse an amount typed by a user, e.g. "50000" or "50.000".

    Dots and spaces are accepted as thousand separators. Decimal parts,
    negative numbers and zero are rejected with ValueError.
    """
    cleaned = text.strip().replace(" ", "").removesuffix("đ")
    if not cleaned:
        raise ValueError("Số tiền không được để trống.")
    if "," in cleaned:
        raise ValueError("Số tiền phải là số nguyên đồng.")
    if "." in cleaned:
        groups = cleaned.split(".")
        if any(len(group) != 3 for group in groups[1:]) or not groups[0]:
            raise ValueError("Dấu chấm chỉ dùng để tách hàng nghìn, ví dụ 50.000.")
        cleaned = "".join(groups)
    if not cleaned.isdigit():
        raise ValueError("Số tiền chỉ được chứa chữ số.")
    amount = int(cleaned)
    if amount <= 0:
        raise ValueError("Số tiền phải lớn hơn 0.")
    return amount


def format_vnd(amount: int) -> str:
    """Format an amount for display: 1234567 becomes "1.234.567 đ"."""
    sign = "-" if amount < 0 else ""
    digits = f"{abs(amount):,}".replace(",", ".")
    return f"{sign}{digits} đ"


def round_vnd(amount: int) -> int:
    """Round an amount to the nearest thousand dong.

    Used for figures shown in summaries, where exact dong are just noise.
    """
    return amount // 1000 * 1000
