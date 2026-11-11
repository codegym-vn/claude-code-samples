"""Fund balance, monthly report and the list of members with unpaid dues."""

import sqlite3

from app.dates import current_month_key, month_key, month_range, parse_month
from app.models import EXPENSE_ACTIVE, INCOME_DUES, Expense, Income, Member
from app.money import round_vnd
from app.services.members import count_active_members, count_members_in_period


def total_income(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM incomes").fetchone()
    return row["total"]


def fund_balance(conn: sqlite3.Connection) -> int:
    """Money currently in the fund: every income minus every expense."""
    spent = conn.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM expenses").fetchone()
    return total_income(conn) - spent["total"]


def monthly_report(conn: sqlite3.Connection, year: int, month: int) -> dict:
    """Income and expense figures for one calendar month."""
    first_day, last_day = month_range(year, month)
    start, end = first_day.isoformat(), last_day.isoformat()

    incomes = [
        Income.from_row(row)
        for row in conn.execute(
            """
            SELECT i.*, m.full_name AS member_name
            FROM incomes i LEFT JOIN members m ON m.id = i.member_id
            WHERE i.received_on >= ? AND i.received_on < ?
            ORDER BY i.received_on, i.id
            """,
            (start, end),
        )
    ]
    expenses = [
        Expense.from_row(row)
        for row in conn.execute(
            """
            SELECT * FROM expenses
            WHERE status = ? AND spent_on >= ? AND spent_on < ?
            ORDER BY spent_on, id
            """,
            (EXPENSE_ACTIVE, start, end),
        )
    ]

    income_total = sum(i.amount for i in incomes)
    expense_total = sum(e.amount for e in expenses)
    dues_total = sum(i.amount for i in incomes if i.kind == INCOME_DUES)

    by_category: dict[str, int] = {}
    for expense in expenses:
        by_category[expense.category] = by_category.get(expense.category, 0) + expense.amount

    members_in_month = count_members_in_period(conn, start, end)
    average_per_member = round_vnd(income_total // members_in_month) if members_in_month else 0

    return {
        "month": month_key(year, month),
        "first_day": first_day,
        "last_day": last_day,
        "incomes": incomes,
        "expenses": expenses,
        "total_income": income_total,
        "total_dues": dues_total,
        "total_donations": income_total - dues_total,
        "total_expense": expense_total,
        "net": income_total - expense_total,
        "by_category": sorted(by_category.items(), key=lambda item: -item[1]),
        "members_in_month": members_in_month,
        "average_per_member": average_per_member,
    }


def unpaid_members(conn: sqlite3.Connection, dues_month: str) -> list[Member]:
    """Members who have no dues payment recorded for the given month."""
    year, month = parse_month(dues_month)
    rows = conn.execute(
        """
        SELECT m.* FROM members m
        WHERE NOT EXISTS (
            SELECT 1 FROM incomes i
            WHERE i.member_id = m.id AND i.kind = ? AND i.dues_month = ?
        )
        ORDER BY m.full_name
        """,
        (INCOME_DUES, month_key(year, month)),
    ).fetchall()
    return [Member.from_row(row) for row in rows]


def dues_by_member(conn: sqlite3.Connection, year: int) -> list[dict]:
    """Dues paid by every member during one year, for the yearly spreadsheet."""
    rows = conn.execute(
        """
        SELECT m.full_name, m.student_code, m.status,
               COUNT(i.id) AS months_paid,
               COALESCE(SUM(i.amount), 0) AS total_paid
        FROM members m
        LEFT JOIN incomes i
          ON i.member_id = m.id AND i.kind = ? AND i.received_on LIKE ?
        GROUP BY m.id
        ORDER BY m.full_name
        """,
        (INCOME_DUES, f"{year:04d}-%"),
    ).fetchall()
    return [dict(row) for row in rows]


def dashboard_summary(conn: sqlite3.Connection) -> dict:
    """Figures for the home page."""
    month = current_month_key()
    report = monthly_report(conn, *parse_month(month))
    return {
        "month": month,
        "balance": fund_balance(conn),
        "month_income": report["total_income"],
        "month_expense": report["total_expense"],
        "unpaid_count": len(unpaid_members(conn, month)),
        "active_members": count_active_members(conn),
    }
