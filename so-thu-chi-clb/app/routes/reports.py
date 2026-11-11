import csv
import io
import sqlite3

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, Response

from app.auth import ROLE_TREASURER, User, get_current_user, require_role
from app.config import DUES_EXPORT_TOKEN
from app.dates import current_month_key, month_key, next_month, parse_month, previous_month, today
from app.db import get_db
from app.models import MEMBER_ACTIVE
from app.services.reports import dues_by_member, monthly_report, unpaid_members
from app.templating import flash, render

router = APIRouter(prefix="/reports")


def _resolve_month(request: Request, month: str) -> tuple[int, int] | None:
    try:
        return parse_month(month or current_month_key())
    except ValueError as exc:
        flash(request, str(exc), "error")
        return None


@router.get("/monthly")
def report_monthly(
    request: Request,
    month: str = "",
    user: User = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    require_role(user, ROLE_TREASURER)
    resolved = _resolve_month(request, month)
    if resolved is None:
        return RedirectResponse("/reports/monthly", status_code=303)
    year, mon = resolved
    report = monthly_report(conn, year, mon)
    context = {
        "report": report,
        "prev_month": month_key(*previous_month(year, mon)),
        "next_month": month_key(*next_month(year, mon)),
    }
    return render(request, "reports/monthly.html", context, user=user)


@router.get("/unpaid")
def report_unpaid(
    request: Request,
    month: str = "",
    user: User = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    require_role(user, ROLE_TREASURER)
    resolved = _resolve_month(request, month)
    if resolved is None:
        return RedirectResponse("/reports/unpaid", status_code=303)
    key = month_key(*resolved)
    members = unpaid_members(conn, key)
    return render(request, "reports/unpaid.html", {"month": key, "members": members}, user=user)


@router.get("/dues.csv")
def report_dues_csv(
    request: Request,
    year: int = 0,
    token: str = "",
    conn: sqlite3.Connection = Depends(get_db),
):
    """Yearly dues sheet. Spreadsheet tools pass ?token= because they cannot log in."""
    if token != DUES_EXPORT_TOKEN:
        get_current_user(request)
    year = year or today().year
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Họ tên", "Mã sinh viên", "Trạng thái", "Số tháng đã đóng", "Tổng đã đóng"])
    for row in dues_by_member(conn, year):
        status = "Đang sinh hoạt" if row["status"] == MEMBER_ACTIVE else "Đã rời"
        writer.writerow(
            [row["full_name"], row["student_code"], status, row["months_paid"], row["total_paid"]]
        )
    # utf-8-sig adds the BOM so Excel on Windows shows Vietnamese correctly.
    body = buffer.getvalue().encode("utf-8")
    return Response(
        body,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="dong-quy-{year}.csv"'},
    )
