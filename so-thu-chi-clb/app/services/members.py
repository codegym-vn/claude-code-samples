"""Member management: listing, searching, joining and leaving the club."""

import re
import sqlite3

from app.dates import parse_iso_date, today
from app.models import INCOME_DUES, MEMBER_ACTIVE, MEMBER_LEFT, Member

STUDENT_CODE_PATTERN = re.compile(r"^[A-Z]{2}\d{6,8}$")


class MemberError(ValueError):
    """Raised when member data is invalid or an action is not allowed."""


def list_members(conn: sqlite3.Connection, include_left: bool = True) -> list[Member]:
    sql = "SELECT * FROM members"
    params: tuple = ()
    if not include_left:
        sql += " WHERE status = ?"
        params = (MEMBER_ACTIVE,)
    sql += " ORDER BY full_name"
    return [Member.from_row(row) for row in conn.execute(sql, params)]


def get_member(conn: sqlite3.Connection, member_id: int) -> Member | None:
    row = conn.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()
    return Member.from_row(row) if row else None


def search_members(conn: sqlite3.Connection, query: str) -> list[Member]:
    """Find members whose name or student code contains the query text."""
    query = query.strip()
    members = list_members(conn)
    if not query:
        return members
    return [m for m in members if query in m.full_name or query in m.student_code]


def count_active_members(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM members WHERE status = ?", (MEMBER_ACTIVE,)
    ).fetchone()
    return row["n"]


def count_members_in_period(conn: sqlite3.Connection, first_day: str, last_day: str) -> int:
    """Members who belonged to the club at some point between the two ISO dates."""
    row = conn.execute(
        """
        SELECT COUNT(*) AS n FROM members
        WHERE joined_on <= ? AND (left_on IS NULL OR left_on >= ?)
        """,
        (last_day, first_day),
    ).fetchone()
    return row["n"]


def create_member(
    conn: sqlite3.Connection, full_name: str, student_code: str, joined_on: str
) -> Member:
    full_name = " ".join(full_name.split())
    student_code = student_code.strip().upper()
    if len(full_name) < 2:
        raise MemberError("Họ tên phải có ít nhất 2 ký tự.")
    if not STUDENT_CODE_PATTERN.match(student_code):
        raise MemberError("Mã sinh viên gồm 2 chữ cái và 6 đến 8 chữ số, ví dụ SV2024001.")
    try:
        joined = parse_iso_date(joined_on)
    except ValueError as exc:
        raise MemberError(str(exc)) from exc
    if joined > today():
        raise MemberError("Ngày tham gia không được ở tương lai.")

    existing = conn.execute(
        "SELECT id FROM members WHERE student_code = ?", (student_code,)
    ).fetchone()
    if existing:
        raise MemberError(f"Mã sinh viên {student_code} đã có trong danh sách.")

    cur = conn.execute(
        "INSERT INTO members (full_name, student_code, joined_on, status) VALUES (?, ?, ?, ?)",
        (full_name, student_code, joined.isoformat(), MEMBER_ACTIVE),
    )
    conn.commit()
    member = get_member(conn, cur.lastrowid)
    assert member is not None
    return member


def mark_left(conn: sqlite3.Connection, member_id: int, left_on: str | None = None) -> Member:
    """Record that a member has left the club. Their history is kept."""
    member = get_member(conn, member_id)
    if member is None:
        raise MemberError("Không tìm thấy thành viên.")
    if not member.is_active:
        raise MemberError("Thành viên này đã rời câu lạc bộ.")
    left_date = parse_iso_date(left_on) if left_on else today()
    if left_date.isoformat() < member.joined_on:
        raise MemberError("Ngày rời không được trước ngày tham gia.")
    conn.execute(
        "UPDATE members SET status = ?, left_on = ? WHERE id = ?",
        (MEMBER_LEFT, left_date.isoformat(), member_id),
    )
    conn.commit()
    updated = get_member(conn, member_id)
    assert updated is not None
    return updated


def member_dues_summary(conn: sqlite3.Connection, member_id: int) -> dict:
    """Dues history of one member: total paid and the months covered."""
    rows = conn.execute(
        """
        SELECT dues_month, amount, received_on
        FROM incomes
        WHERE member_id = ? AND kind = ?
        ORDER BY dues_month
        """,
        (member_id, INCOME_DUES),
    ).fetchall()
    return {
        "total_paid": sum(row["amount"] for row in rows),
        "months_paid": [row["dues_month"] for row in rows],
        "payments": [dict(row) for row in rows],
    }
