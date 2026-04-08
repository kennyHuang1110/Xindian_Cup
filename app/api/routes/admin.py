"""Admin endpoints for team bootstrap and blacklist management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin_token
from app.models.blacklist import Blacklist
from app.models.team import Team, TeamStatus
from app.schemas.blacklist import BlacklistCreate, BlacklistRead
from app.schemas.team import TeamAdminCreate, TeamAdminUpdate, TeamRead

router = APIRouter()


@router.post("/teams", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(
    payload: TeamAdminCreate,
    _: None = Depends(require_admin_token),
    db: Session = Depends(get_db),
) -> Team:
    """Create a team and initial captain data from the admin backend."""
    team = Team(**payload.model_dump(), status=TeamStatus.PENDING)
    try:
        db.add(team)
        db.commit()
        db.refresh(team)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Team name or captain email already exists.",
        ) from None
    return team


@router.patch("/teams/{team_id}", response_model=TeamRead)
def update_team(
    team_id: int,
    payload: TeamAdminUpdate,
    _: None = Depends(require_admin_token),
    db: Session = Depends(get_db),
) -> Team:
    """Update admin-managed team metadata."""
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(team, field, value)
    try:
        db.add(team)
        db.commit()
        db.refresh(team)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Team name or captain email already exists.",
        ) from None
    return team


@router.post("/blacklist", response_model=BlacklistRead, status_code=status.HTTP_201_CREATED)
def create_blacklist_entry(
    payload: BlacklistCreate,
    _: None = Depends(require_admin_token),
    db: Session = Depends(get_db),
) -> Blacklist:
    """Create a blacklist entry reserved for future enforcement logic."""
    entry = Blacklist(**payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
