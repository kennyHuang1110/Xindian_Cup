"""FastAPI application entrypoint for the public static site."""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
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

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/gallery", StaticFiles(directory="img"), name="gallery")
templates = Jinja2Templates(directory="app/templates")


def build_schedule_columns(schedule: dict[str, object]) -> dict[str, object]:
    """Build a three-court schedule matrix for template rendering."""
    courts = ["場地 1", "場地 2", "場地 3"]
    rows: list[dict[str, object]] = []

    time_slots: dict[str, dict[str, object]] = {}
    notes: list[dict[str, str]] = []

    for match in schedule["matches"]:
        time = match["time"]
        court = match["court"]
        if court not in courts:
            notes.append(match)
            continue

        if time not in time_slots:
            time_slots[time] = {"time": time, "slots": {name: None for name in courts}}

        time_slots[time]["slots"][court] = match

    for item in time_slots.values():
        rows.append(
            {
                "time": item["time"],
                "slots": [item["slots"][court] for court in courts],
            }
        )

    return {"courts": courts, "rows": rows, "notes": notes}


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


@app.get("/", response_class=HTMLResponse, tags=["pages"])
async def index(request: Request) -> HTMLResponse:
    """Render the public landing page."""
    site_content = load_site_content()
    return render_page(
        request,
        "index.html",
        {
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
    schedule = load_site_content()["schedule"]
    return render_page(
        request,
        "schedule.html",
        {
            "schedule": schedule,
            "schedule_columns": build_schedule_columns(schedule),
        },
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
