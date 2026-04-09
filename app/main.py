"""FastAPI application entrypoint for the static gated site."""

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.router import api_router
from app.core.config import get_settings
from app.services.site_content import (
    get_gallery_photos,
    get_logo_filename,
    load_charter,
    load_site_content,
)

settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/gallery", StaticFiles(directory="img"), name="gallery")
templates = Jinja2Templates(directory="app/templates")

PROTECTED_PATHS = {"/", "/public/teams", "/history/photos", "/charter", "/schedule"}
OPEN_PREFIXES = ("/static", "/gallery", "/health", "/api", "/docs", "/openapi.json", "/redoc")


def is_line_access_allowed(line_user_id: str) -> bool:
    """Check whether the given LINE user id can access the static site."""
    allowed_ids = settings.parsed_line_login_allowed_ids
    if not allowed_ids:
        return bool(line_user_id.strip())
    return line_user_id.strip() in allowed_ids


@app.middleware("http")
async def line_gate(request: Request, call_next):
    """Require a LINE gate cookie before showing protected pages."""
    path = request.url.path
    if path == "/line/login" or path == "/line/logout" or path.startswith(OPEN_PREFIXES):
        return await call_next(request)
    if path in PROTECTED_PATHS and not request.cookies.get(settings.line_login_cookie_name):
        return RedirectResponse(url="/line/login", status_code=303)
    return await call_next(request)


def render_page(request: Request, template_name: str, context: dict[str, object]) -> HTMLResponse:
    """Render a page template with shared site context."""
    return templates.TemplateResponse(
        request,
        template_name,
        {
            "app_name": settings.app_name,
            "logo_filename": get_logo_filename(),
            **context,
        },
    )


@app.get("/line/login", response_class=HTMLResponse, tags=["pages"])
async def line_login_page(request: Request) -> HTMLResponse:
    """Render the LINE gate page."""
    return render_page(
        request,
        "line_login.html",
        {
            "error_message": None,
            "allowed_ids_configured": bool(settings.parsed_line_login_allowed_ids),
        },
    )


@app.post("/line/login", response_class=HTMLResponse, tags=["pages"])
async def line_login_submit(request: Request, line_user_id: str = Form(...)) -> HTMLResponse:
    """Accept a simplified LINE login and set the access cookie."""
    line_user_id = line_user_id.strip()
    if not is_line_access_allowed(line_user_id):
        return render_page(
            request,
            "line_login.html",
            {
                "error_message": "這組 LINE user id 不在允許名單內，請確認後再試。",
                "allowed_ids_configured": bool(settings.parsed_line_login_allowed_ids),
            },
        )

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        settings.line_login_cookie_name,
        line_user_id,
        httponly=True,
        samesite="lax",
        max_age=settings.session_expire_hours * 3600,
    )
    return response


@app.post("/line/logout", response_class=RedirectResponse, tags=["pages"])
async def line_logout() -> RedirectResponse:
    """Clear the LINE gate cookie."""
    response = RedirectResponse(url="/line/login", status_code=303)
    response.delete_cookie(settings.line_login_cookie_name)
    return response


@app.get("/", response_class=HTMLResponse, tags=["pages"])
async def index(request: Request) -> HTMLResponse:
    """Render the gated landing page."""
    site_content = load_site_content()
    return render_page(
        request,
        "index.html",
        {
            "hero_title": site_content["hero_title"],
            "hero_subtitle": site_content["hero_subtitle"],
            "hero_description": site_content["hero_description"],
            "team_count": len(site_content["teams"]),
        },
    )


@app.get("/public/teams", response_class=HTMLResponse, tags=["pages"])
async def public_teams_page(request: Request) -> HTMLResponse:
    """Render the static roster page."""
    return render_page(
        request,
        "public_teams.html",
        {"teams": load_site_content()["teams"]},
    )


@app.get("/schedule", response_class=HTMLResponse, tags=["pages"])
async def schedule_page(request: Request) -> HTMLResponse:
    """Render the static schedule page."""
    return render_page(
        request,
        "schedule.html",
        {"schedule": load_site_content()["schedule"]},
    )


@app.get("/history/photos", response_class=HTMLResponse, tags=["pages"])
async def history_photos(request: Request) -> HTMLResponse:
    """Render the history gallery page."""
    return render_page(
        request,
        "history_gallery.html",
        {"gallery_photos": get_gallery_photos()},
    )


@app.get("/charter", response_class=HTMLResponse, tags=["pages"])
async def charter_page(request: Request) -> HTMLResponse:
    """Render the charter page."""
    return render_page(
        request,
        "charter.html",
        {"charter": load_charter()},
    )


app.include_router(api_router)
