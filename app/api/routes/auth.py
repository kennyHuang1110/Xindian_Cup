"""Authentication-related endpoints."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.models.session import Session as CaptainSession
from app.models.team import Team, TeamStatus
from app.schemas.auth import LineEntryRequest, LineEntryResponse
from app.services.auth import ensure_not_blacklisted, utcnow
from app.services.security import generate_token, hash_token

router = APIRouter()
settings = get_settings()


@router.post("/line-entry", response_model=LineEntryResponse)
def line_entry(payload: LineEntryRequest, db: Session = Depends(get_db)) -> LineEntryResponse:
    """Validate a captain LINE entry and issue a session token."""
    team = db.get(Team, payload.team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")
    if team.captain_line_user_id != payload.line_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="LINE user is not assigned to this captain.",
        )
    if team.status != TeamStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Captain account is not active yet.",
        )

    ensure_not_blacklisted(db, "line_user_id", payload.line_user_id)
    ensure_not_blacklisted(db, "email", team.captain_email)

    raw_token = generate_token(24)
    expires_at = utcnow() + timedelta(hours=settings.session_expire_hours)
    session = CaptainSession(
        team_id=team.id,
        line_user_id=payload.line_user_id,
        session_token_hash=hash_token(raw_token),
        expires_at=expires_at,
    )
    db.add(session)
    db.commit()
    return LineEntryResponse(
        ok=True,
        message="Captain session created.",
        team_id=payload.team_id,
        line_user_id=payload.line_user_id,
        session_token=raw_token,
        expires_at=expires_at,
    )
