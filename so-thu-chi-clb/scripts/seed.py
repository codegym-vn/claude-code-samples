"""Load demo data: members, dues, donations and expenses for recent months.

Usage:
    python -m scripts.seed           # only when the database is empty
    python -m scripts.seed --reset   # wipe all rows first, then seed

Dates are relative to today so the demo always has "this month" data.
"""

import argparse
import random
from datetime import date

from app.config import MONTHLY_DUES, get_settings
from app.dates import month_key, month_range, previous_month, today
from app.db import connect, init_db
from app.services import ledger, members

TREASURER = "thuquy"

MEMBERS = [
    ("Nguyễn Văn An", "SV2023001"),
    ("Trần Thị Bích Ngọc", "SV2023002"),
    ("Lê Hoàng Long", "SV2023003"),
    ("Phạm Thu Trang", "SV2023004"),
    ("Hoàng Minh Đức", "SV2023005"),
    ("Vũ Thị Lan", "SV2023006"),
    ("Đặng Quốc Bảo", "SV2023007"),
    ("Bùi Thanh Hương", "SV2023008"),
    ("Đỗ Gia Huy", "SV2024009"),
    ("Ngô Phương Anh", "SV2024010"),
    ("Dương Văn Tú", "SV2024011"),
    ("An Khánh Linh", "SV2024012"),
]

# (category, description, amount) picked from each month.
EXPENSE_TEMPLATES = [
    ("Văn phòng phẩm", "Mua bút và giấy cho buổi sinh hoạt", 85_000),
    ("Nước uống", "Nước uống buổi sinh hoạt định kỳ", 120_000),
    ("In ấn", "In poster tuyển thành viên", 150_000),
    ("Sự kiện", "Thuê loa cho buổi giao lưu", 300_000),
    ("Thuê phòng", "Thuê phòng họp ngoài giờ", 200_000),
    ("Khác", "Phí chuyển khoản ngân hàng", 11_000),
]


def _wipe(conn) -> None:
    for table in ("incomes", "expenses", "members"):
        conn.execute(f"DELETE FROM {table}")
    conn.execute("DELETE FROM sqlite_sequence")
    conn.commit()


def _months_to_seed(count: int = 4) -> list[tuple[int, int]]:
    """The current month plus the ``count - 1`` months before it, oldest first."""
    t = today()
    months = [(t.year, t.month)]
    for _ in range(count - 1):
        months.append(previous_month(*months[-1]))
    return list(reversed(months))


def _clamp(d: date) -> date:
    return min(d, today())


def seed(reset: bool = False) -> None:
    settings = get_settings()
    init_db(settings.database_path)
    conn = connect(settings.database_path)
    rng = random.Random(2024)
    try:
        existing = conn.execute("SELECT COUNT(*) FROM members").fetchone()[0]
        if existing and not reset:
            print("Cơ sở dữ liệu đã có dữ liệu. Dùng --reset để nạp lại từ đầu.")
            return
        if reset:
            _wipe(conn)

        months = _months_to_seed()
        first_month_start = month_range(*months[0])[0]
        created = [
            members.create_member(conn, name, code, first_month_start.isoformat())
            for name, code in MEMBERS
        ]

        # Two members leave during the previous month.
        prev_year, prev_month = months[-2]
        leave_day = month_range(prev_year, prev_month)[0].replace(day=20).isoformat()
        leavers = {created[6].id, created[10].id}
        for member_id in leavers:
            members.mark_left(conn, member_id, leave_day)

        for year, month in months:
            first, last = month_range(year, month)
            is_current = (year, month) == months[-1]
            key = month_key(year, month)

            # Dues: most members pay; a few pay on the last day of the month.
            for index, member in enumerate(created):
                if member.id in leavers and (year, month) >= (prev_year, prev_month):
                    continue
                if rng.random() < 0.15:
                    continue
                if not is_current and index % 4 == 0:
                    paid_on = last
                else:
                    paid_on = _clamp(first.replace(day=rng.randint(1, 10)))
                if is_current and paid_on > today():
                    continue
                ledger.create_income(
                    conn,
                    received_on=paid_on.isoformat(),
                    amount=MONTHLY_DUES,
                    kind="dues",
                    member_id=member.id,
                    dues_month=key,
                    created_by=TREASURER,
                )

            # One donation per past month, received on the last day.
            if not is_current:
                ledger.record_donation(
                    conn,
                    received_on=last.isoformat(),
                    amount=rng.choice([200_000, 300_000, 500_000]),
                    note="Ủng hộ của cựu thành viên",
                    created_by=TREASURER,
                )

            # Expenses spread over the month.
            for category, description, amount in rng.sample(EXPENSE_TEMPLATES, 3):
                spent_on = _clamp(first.replace(day=rng.randint(5, 25)))
                ledger.create_expense(
                    conn,
                    spent_on=spent_on.isoformat(),
                    amount=amount,
                    category=category,
                    description=description,
                    created_by=TREASURER,
                )
            if not is_current:
                last_day_expense = ledger.create_expense(
                    conn,
                    spent_on=last.isoformat(),
                    amount=175_000,
                    category="Sự kiện",
                    description="Liên hoan cuối tháng",
                    created_by=TREASURER,
                )
                if (year, month) == months[0]:
                    ledger.cancel_expense(conn, last_day_expense.id, "Ghi trùng, đã nhập ở tháng sau")

        # A mistaken expense that was cancelled.
        wrong = ledger.create_expense(
            conn,
            spent_on=_clamp(month_range(prev_year, prev_month)[0].replace(day=12)).isoformat(),
            amount=1_500_000,
            category="Sự kiện",
            description="Đặt cọc thuê xe dã ngoại",
            created_by=TREASURER,
        )
        ledger.cancel_expense(conn, wrong.id, "Chuyến dã ngoại bị hoãn, nhà xe đã hoàn tiền")

        print(f"Đã nạp {len(created)} thành viên và dữ liệu thu chi của {len(months)} tháng.")
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Nạp dữ liệu mẫu cho sổ thu chi.")
    parser.add_argument("--reset", action="store_true", help="xóa dữ liệu hiện có trước khi nạp")
    args = parser.parse_args()
    seed(reset=args.reset)


if __name__ == "__main__":
    main()
