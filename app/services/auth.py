"""Session and access helpers for captain authentication."""

from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.blacklist import Blacklist
from app.models.email_verification import EmailVerification
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


def is_team_email_verified(db: Session, team_id: int) -> bool:
    """Return whether the team's captain email has been verified."""
    stmt = (
        select(EmailVerification)
        .where(EmailVerification.team_id == team_id)
        .where(EmailVerification.used_at.is_not(None))
        .order_by(EmailVerification.created_at.desc())
    )
    return db.scalars(stmt).first() is not None


def get_captain_session_by_token(
    db: Session,
    raw_token: str,
    *,
    require_active_team: bool = False,
) -> tuple[CaptainSession, Team]:
    """Resolve a captain session and team from a raw token value."""
    token_hash = hash_token(raw_token)
    stmt = select(CaptainSession).where(CaptainSession.session_token_hash == token_hash)
    session = db.scalars(stmt).first()
    if session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session token.")
    if _as_utc(session.expires_at) < utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired.")

    team = db.get(Team, session.team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")
    if team.status == TeamStatus.DISABLED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Captain account is disabled.",
        )
    if require_active_team and team.status != TeamStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Captain account is not active.",
        )

    ensure_not_blacklisted(db, "line_user_id", session.line_user_id)
    if team.captain_email:
        ensure_not_blacklisted(db, "email", team.captain_email)

    return session, team


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
    return get_captain_session_by_token(db, credentials.credentials, require_active_team=False)
