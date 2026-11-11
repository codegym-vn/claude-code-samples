"""Income and expense entries."""

import sqlite3

from app.dates import month_key, month_range, parse_iso_date, parse_month, today
from app.models import (
    EXPENSE_ACTIVE,
    EXPENSE_CANCELLED,
    INCOME_DONATION,
    INCOME_DUES,
    INCOME_KIND_LABELS,
    Expense,
    Income,
)
from app.services.members import get_member


class LedgerError(ValueError):
    """Raised when an income or expense cannot be recorded or changed."""


def _check_entry_date(text: str) -> str:
    try:
        d = parse_iso_date(text)
    except ValueError as exc:
        raise LedgerError(str(exc)) from exc
    if d > today():
        raise LedgerError("Không ghi sổ cho ngày ở tương lai.")
    return d.isoformat()


# ---------------------------------------------------------------- incomes


def create_income(
    conn: sqlite3.Connection,
    *,
    received_on: str,
    amount: int,
    kind: str,
    created_by: str,
    member_id: int | None = None,
    dues_month: str | None = None,
    note: str = "",
) -> Income:
    if kind not in INCOME_KIND_LABELS:
        raise LedgerError("Loại khoản thu không hợp lệ.")
    if not isinstance(amount, int) or amount <= 0:
        raise LedgerError("Số tiền phải là số nguyên dương.")
    received = _check_entry_date(received_on)

    if kind == INCOME_DUES:
        if member_id is None:
            raise LedgerError("Khoản quỹ tháng phải gắn với một thành viên.")
        member = get_member(conn, member_id)
        if member is None:
            raise LedgerError("Không tìm thấy thành viên.")
        if not dues_month:
            raise LedgerError("Hãy chọn tháng đóng quỹ.")
        try:
            year, month = parse_month(dues_month)
        except ValueError as exc:
            raise LedgerError(str(exc)) from exc
        dues_month = month_key(year, month)
        duplicate = conn.execute(
            "SELECT id FROM incomes WHERE kind = ? AND member_id = ? AND dues_month = ?",
            (INCOME_DUES, member_id, dues_month),
        ).fetchone()
        if duplicate:
            raise LedgerError(f"{member.full_name} đã đóng quỹ tháng {dues_month}.")
    else:
        dues_month = None

    cur = conn.execute(
        """
        INSERT INTO incomes (received_on, amount, kind, member_id, dues_month, note, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (received, amount, kind, member_id, dues_month, note.strip(), created_by),
    )
    conn.commit()
    return get_income(conn, cur.lastrowid)


def get_income(conn: sqlite3.Connection, income_id: int) -> Income:
    row = conn.execute(
        """
        SELECT i.*, m.full_name AS member_name
        FROM incomes i LEFT JOIN members m ON m.id = i.member_id
        WHERE i.id = ?
        """,
        (income_id,),
    ).fetchone()
    if row is None:
        raise LedgerError("Không tìm thấy khoản thu.")
    return Income.from_row(row)


def list_incomes(conn: sqlite3.Connection, month: str | None = None) -> list[Income]:
    """All incomes, newest first. ``month`` ("YYYY-MM") limits to one month."""
    sql = """
        SELECT i.*, m.full_name AS member_name
        FROM incomes i LEFT JOIN members m ON m.id = i.member_id
    """
    params: tuple = ()
    if month:
        first, last = month_range(*parse_month(month))
        sql += " WHERE i.received_on BETWEEN ? AND ?"
        params = (first.isoformat(), last.isoformat())
    sql += " ORDER BY i.received_on DESC, i.id DESC"
    return [Income.from_row(row) for row in conn.execute(sql, params)]


def record_donation(
    conn: sqlite3.Connection, *, received_on: str, amount: int, note: str, created_by: str
) -> Income:
    return create_income(
        conn,
        received_on=received_on,
        amount=amount,
        kind=INCOME_DONATION,
        note=note,
        created_by=created_by,
    )


# --------------------------------------------------------------- expenses


def create_expense(
    conn: sqlite3.Connection,
    *,
    spent_on: str,
    amount: int,
    category: str,
    description: str,
    created_by: str,
) -> Expense:
    if not isinstance(amount, int) or amount <= 0:
        raise LedgerError("Số tiền phải là số nguyên dương.")
    spent = _check_entry_date(spent_on)
    description = description.strip()
    if not description:
        raise LedgerError("Hãy ghi nội dung khoản chi.")
    category = category.strip() or "Khác"

    cur = conn.execute(
        """
        INSERT INTO expenses (spent_on, amount, category, description, status, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (spent, amount, category, description, EXPENSE_ACTIVE, created_by),
    )
    conn.commit()
    return get_expense(conn, cur.lastrowid)


def get_expense(conn: sqlite3.Connection, expense_id: int) -> Expense:
    row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    if row is None:
        raise LedgerError("Không tìm thấy khoản chi.")
    return Expense.from_row(row)


def list_expenses(conn: sqlite3.Connection, include_cancelled: bool = True) -> list[Expense]:
    sql = "SELECT * FROM expenses"
    params: tuple = ()
    if not include_cancelled:
        sql += " WHERE status = ?"
        params = (EXPENSE_ACTIVE,)
    sql += " ORDER BY spent_on DESC, id DESC"
    return [Expense.from_row(row) for row in conn.execute(sql, params)]


def total_active_expenses(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE status = ?",
        (EXPENSE_ACTIVE,),
    ).fetchone()
    return row["total"]


def cancel_expense(conn: sqlite3.Connection, expense_id: int, note: str = "") -> Expense:
    """Mark an expense as cancelled. Entries are never deleted from the ledger."""
    expense = get_expense(conn, expense_id)
    if expense.is_cancelled:
        raise LedgerError("Khoản chi này đã được hủy trước đó.")
    conn.execute(
        "UPDATE expenses SET status = ?, cancelled_on = ?, cancel_note = ? WHERE id = ?",
        (EXPENSE_CANCELLED, today().isoformat(), note.strip(), expense_id),
    )
    conn.commit()
    return get_expense(conn, expense_id)
