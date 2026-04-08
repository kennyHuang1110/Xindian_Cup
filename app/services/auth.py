"""Session and access helpers for captain authentication."""

from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.blacklist import Blacklist
from app.models.session import Session as CaptainSession
from app.models.team import Team, TeamStatus
from app.services.security import hash_token

bearer_scheme = HTTPBearer(auto_error=False)


def utcnow() -> datetime:
    """Return an aware UTC timestamp."""
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    """Normalize DB datetimes to aware UTC values."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def ensure_not_blacklisted(db: Session, entry_type: str, value: str) -> None:
    """Reject access for active blacklist entries."""
    stmt = (
        select(Blacklist)
        .where(Blacklist.type == entry_type)
        .where(Blacklist.value == value)
        .where(Blacklist.is_active.is_(True))
    )
    entry = db.scalars(stmt).first()
    if entry:
        reason = entry.reason or "Blocked by blacklist."
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=reason)


def get_current_captain_session(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> tuple[CaptainSession, Team]:
    """Resolve the current captain session and owning team from a bearer token."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Captain session token is required.",
        )

    token_hash = hash_token(credentials.credentials)
    stmt = select(CaptainSession).where(CaptainSession.session_token_hash == token_hash)
    session = db.scalars(stmt).first()
    if session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token.")
    if _as_utc(session.expires_at) < utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired.")

    team = db.get(Team, session.team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")
    if team.status != TeamStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Captain account is not active.",
        )

    ensure_not_blacklisted(db, "line_user_id", session.line_user_id)
    if team.captain_email:
        ensure_not_blacklisted(db, "email", team.captain_email)

    return session, team
