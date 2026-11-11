import sqlite3

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from app.auth import ROLE_TREASURER, User, get_current_user, require_role
from app.config import MONTHLY_DUES
from app.dates import current_month_key, today
from app.db import get_db
from app.models import INCOME_DUES, INCOME_KIND_LABELS
from app.money import parse_vnd
from app.services.ledger import LedgerError, create_income, list_incomes
from app.services.members import list_members
from app.templating import flash, render

router = APIRouter(prefix="/incomes")


@router.get("")
def income_list(
    request: Request,
    month: str = "",
    user: User = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    try:
        incomes = list_incomes(conn, month or None)
    except ValueError as exc:
        flash(request, str(exc), "error")
        return RedirectResponse("/incomes", status_code=303)
    total = sum(i.amount for i in incomes)
    return render(
        request,
        "incomes/list.html",
        {"incomes": incomes, "month": month, "total": total},
        user=user,
    )


def _form_context(conn: sqlite3.Connection, form: dict, error: str | None = None) -> dict:
    return {
        "form": form,
        "error": error,
        "members": list_members(conn, include_left=False),
        "kinds": INCOME_KIND_LABELS,
    }


@router.get("/new")
def new_income_form(
    request: Request,
    user: User = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    require_role(user, ROLE_TREASURER)
    form = {
        "received_on": today().isoformat(),
        "amount": str(MONTHLY_DUES),
        "kind": INCOME_DUES,
        "member_id": "",
        "dues_month": current_month_key(),
        "note": "",
    }
    return render(request, "incomes/new.html", _form_context(conn, form), user=user)


@router.post("/new")
def new_income(
    request: Request,
    received_on: str = Form(""),
    amount: str = Form(""),
    kind: str = Form(INCOME_DUES),
    member_id: str = Form(""),
    dues_month: str = Form(""),
    note: str = Form(""),
    user: User = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    require_role(user, ROLE_TREASURER)
    form = {
        "received_on": received_on,
        "amount": amount,
        "kind": kind,
        "member_id": member_id,
        "dues_month": dues_month,
        "note": note,
    }
    try:
        income = create_income(
            conn,
            received_on=received_on,
            amount=parse_vnd(amount),
            kind=kind,
            member_id=int(member_id) if member_id else None,
            dues_month=dues_month or None,
            note=note,
            created_by=user.username,
        )
    except ValueError as exc:
        return render(
            request, "incomes/new.html", _form_context(conn, form, str(exc)), status_code=400, user=user
        )
    flash(request, f"Đã ghi khoản thu {income.kind_label.lower()}.")
    return RedirectResponse("/incomes", status_code=303)
