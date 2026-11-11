import sqlite3

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.auth import ROLE_TREASURER, User, get_current_user, require_role
from app.config import EXPENSE_CATEGORIES
from app.dates import today
from app.db import get_db
from app.money import parse_vnd
from app.services.ledger import (
    LedgerError,
    cancel_expense,
    create_expense,
    get_expense,
    list_expenses,
    total_active_expenses,
)
from app.templating import flash, render

router = APIRouter(prefix="/expenses")


@router.get("")
def expense_list(
    request: Request,
    user: User = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    expenses = list_expenses(conn)
    return render(
        request,
        "expenses/list.html",
        {"expenses": expenses, "total_active": total_active_expenses(conn)},
        user=user,
    )


@router.get("/new")
def new_expense_form(request: Request, user: User = Depends(get_current_user)):
    require_role(user, ROLE_TREASURER)
    form = {"spent_on": today().isoformat(), "amount": "", "category": "", "description": ""}
    return render(
        request,
        "expenses/new.html",
        {"form": form, "categories": EXPENSE_CATEGORIES},
        user=user,
    )


@router.post("/new")
def new_expense(
    request: Request,
    spent_on: str = Form(""),
    amount: str = Form(""),
    category: str = Form(""),
    description: str = Form(""),
    user: User = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    require_role(user, ROLE_TREASURER)
    try:
        expense = create_expense(
            conn,
            spent_on=spent_on,
            amount=parse_vnd(amount),
            category=category,
            description=description,
            created_by=user.username,
        )
    except ValueError as exc:
        form = {"spent_on": spent_on, "amount": amount, "category": category, "description": description}
        return render(
            request,
            "expenses/new.html",
            {"form": form, "categories": EXPENSE_CATEGORIES, "error": str(exc)},
            status_code=400,
            user=user,
        )
    flash(request, f"Đã ghi khoản chi: {expense.description}.")
    return RedirectResponse("/expenses", status_code=303)


@router.post("/{expense_id}/cancel")
def expense_cancel(
    request: Request,
    expense_id: int,
    note: str = Form(""),
    user: User = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    require_role(user, ROLE_TREASURER)
    try:
        get_expense(conn, expense_id)
    except LedgerError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    try:
        expense = cancel_expense(conn, expense_id, note)
    except LedgerError as exc:
        flash(request, str(exc), "error")
    else:
        flash(request, f"Đã hủy khoản chi: {expense.description}.")
    return RedirectResponse("/expenses", status_code=303)
