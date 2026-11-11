import sqlite3

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.auth import ROLE_TREASURER, User, get_current_user, require_role
from app.dates import current_month_key, month_key, next_month, parse_month, previous_month
from app.db import get_db
from app.services.reports import monthly_report, unpaid_members
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
