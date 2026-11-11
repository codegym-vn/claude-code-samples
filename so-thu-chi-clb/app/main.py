"""Application factory and entry point.

Run locally with:  uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from app.auth import NotAuthenticated
from app.config import BASE_DIR, Settings, get_settings
from app.db import init_db
from app.routes import auth, expenses, home, incomes, members, reports
from app.templating import render


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    init_db(settings.database_path)

    app = FastAPI(title="Sổ thu chi câu lạc bộ")
    app.state.settings = settings
    app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, same_site="lax")
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")

    for module in (auth, home, members, incomes, expenses, reports):
        app.include_router(module.router)

    @app.exception_handler(NotAuthenticated)
    async def redirect_to_login(request: Request, exc: NotAuthenticated):
        return RedirectResponse("/login", status_code=303)

    @app.exception_handler(StarletteHTTPException)
    async def http_error_page(request: Request, exc: StarletteHTTPException):
        titles = {403: "Không có quyền", 404: "Không tìm thấy trang"}
        return render(
            request,
            "error.html",
            {"status": exc.status_code, "title": titles.get(exc.status_code, "Có lỗi"), "detail": exc.detail},
            status_code=exc.status_code,
        )

    return app


app = create_app()
