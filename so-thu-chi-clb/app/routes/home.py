import sqlite3

from fastapi import APIRouter, Depends, Request

from app.auth import User, get_current_user
from app.db import get_db
from app.services.reports import dashboard_summary
from app.templating import render

router = APIRouter()


@router.get("/")
def home(
    request: Request,
    user: User = Depends(get_current_user),
    conn: sqlite3.Connection = Depends(get_db),
):
    return render(request, "home.html", {"summary": dashboard_summary(conn)}, user=user)
