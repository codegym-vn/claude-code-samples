"""Jinja2 setup, template filters and a small render helper."""

from pathlib import Path

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.auth import User, user_from_session
from app.dates import format_date_vn
from app.money import format_vnd, round_vnd

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.filters["vnd"] = format_vnd
templates.env.filters["vnd_rounded"] = lambda amount: format_vnd(round_vnd(amount))
templates.env.filters["date_vn"] = format_date_vn


def flash(request: Request, message: str, category: str = "success") -> None:
    """Queue a one-time message shown on the next rendered page."""
    messages = request.session.get("flash", [])
    messages.append({"message": message, "category": category})
    request.session["flash"] = messages


def render(
    request: Request,
    template_name: str,
    context: dict | None = None,
    status_code: int = 200,
    user: User | None = None,
) -> HTMLResponse:
    data = dict(context or {})
    data["user"] = user or user_from_session(request)
    data["messages"] = request.session.pop("flash", [])
    return templates.TemplateResponse(request, template_name, data, status_code=status_code)
