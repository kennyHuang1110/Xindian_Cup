"""Public endpoints backed by static site content."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.site_content import get_logo_filename, load_site_content

router = APIRouter()
page_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/teams")
def list_public_teams() -> list[dict[str, object]]:
    """Return static public teams."""
    return load_site_content()["teams"]


@router.get("/teams/detail")
def list_public_teams_detail() -> list[dict[str, object]]:
    """Return static public teams with member details."""
    return load_site_content()["teams"]


@page_router.get("/public/teams", response_class=HTMLResponse, include_in_schema=False)
def public_teams_page(request: Request) -> HTMLResponse:
    """Render the static public team page."""
    content = load_site_content()
    return templates.TemplateResponse(
        request,
        "public_teams.html",
        {
            "teams": content["teams"],
            "app_name": "Xindian_Cup",
            "logo_filename": get_logo_filename(),
        },
    )
