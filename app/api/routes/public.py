"""Public endpoints exposed without captain authentication."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_db
from app.models.team import Team, TeamStatus
from app.schemas.team import PublicTeamDetailRead, PublicTeamRead

router = APIRouter()
page_router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _public_teams_query():
    return (
        select(Team)
        .where(Team.status == TeamStatus.ACTIVE)
        .options(selectinload(Team.members))
        .order_by(Team.team_name)
    )


@router.get("/teams", response_model=list[PublicTeamRead])
def list_public_teams(db: Session = Depends(get_db)) -> list[Team]:
    """Return active teams for public announcement pages."""
    return list(db.scalars(_public_teams_query()).all())


@router.get("/teams/detail", response_model=list[PublicTeamDetailRead])
def list_public_teams_detail(db: Session = Depends(get_db)) -> list[Team]:
    """Return active teams and their public members."""
    return list(db.scalars(_public_teams_query()).all())


@page_router.get("/public/teams", response_class=HTMLResponse, include_in_schema=False)
def public_teams_page(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    """Render a public-facing team and member list page."""
    teams = list(db.scalars(_public_teams_query()).all())
    return templates.TemplateResponse(
        request,
        "public_teams.html",
        {"teams": teams, "app_name": "Xindian_Cup"},
    )
