from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from app.auth import authenticate
from app.templating import flash, render

router = APIRouter()


@router.get("/login")
def login_page(request: Request):
    return render(request, "login.html", {"username": ""})


@router.post("/login")
def login(request: Request, username: str = Form(""), password: str = Form("")):
    user = authenticate(username, password)
    if user is None:
        return render(
            request,
            "login.html",
            {"username": username, "error": "Tên đăng nhập hoặc mật khẩu không đúng."},
            status_code=400,
        )
    request.session["username"] = user.username
    flash(request, f"Xin chào {user.display_name}.")
    return RedirectResponse("/", status_code=303)


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
