"""FastAPI application entrypoint."""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse, tags=["pages"])
async def index(request: Request) -> HTMLResponse:
    """Render the public event landing page."""
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "app_name": settings.app_name,
            "hero_title": "Xindian_Cup",
            "hero_subtitle": "新店盃排球賽報名與公告平台",
        },
    )


@app.get("/captain/manage", response_class=HTMLResponse, tags=["pages"])
async def captain_manage(request: Request) -> HTMLResponse:
    """Render a temporary captain entry page placeholder."""
    return templates.TemplateResponse(
        request,
        "captain_manage.html",
        {"app_name": settings.app_name},
    )


app.include_router(api_router)
