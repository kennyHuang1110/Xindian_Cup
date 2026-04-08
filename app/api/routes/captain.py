"""Captain-facing endpoints guarded by verification state."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.models.email_verification import EmailVerification
from app.models.member import Member
from app.models.team import Team, TeamStatus
from app.schemas.email_verification import (
    EmailVerificationIssueResponse,
    EmailVerificationRequest,
    EmailVerificationStatus,
)
from app.schemas.member import MemberCreate, MemberRead
from app.schemas.team import CaptainProfileRead
from app.services.auth import get_current_captain_session
from app.services.security import generate_token, hash_token

router = APIRouter()
settings = get_settings()


def _as_utc(value: datetime) -> datetime:
    """Normalize datetimes to timezone-aware UTC values."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _get_team_or_404(db: Session, team_id: int) -> Team:
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found.")
    return team


def _ensure_verified(db: Session, team_id: int) -> None:
    stmt = (
        select(EmailVerification)
        .where(EmailVerification.team_id == team_id)
        .where(EmailVerification.used_at.is_not(None))
        .order_by(EmailVerification.created_at.desc())
    )
    verification = db.scalars(stmt).first()
    if verification is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Captain email verification is required.",
        )


@router.post("/send-email-verification", response_model=EmailVerificationIssueResponse)
def send_email_verification(
    payload: EmailVerificationRequest,
    db: Session = Depends(get_db),
) -> EmailVerificationIssueResponse:
    """Create a verification token record for a captain email."""
    team = _get_team_or_404(db, payload.team_id)
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.email_verification_expire_minutes
    )
    if team.captain_email != payload.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification email must match the captain email.",
        )
    raw_token = generate_token(24)
    verification = EmailVerification(
        team_id=team.id,
        email=payload.email,
        token_hash=hash_token(raw_token),
        expires_at=expires_at,
    )
    db.add(verification)
    db.commit()
    return EmailVerificationIssueResponse(
        message="Verification token created for MVP.",
        verification_token=raw_token,
        verification_url=f"{settings.app_base_url}/api/captain/verify-email?token={raw_token}",
    )


@router.get("/verify-email", response_model=EmailVerificationStatus)
def verify_email(
    token: str = Query(..., min_length=8),
    db: Session = Depends(get_db),
) -> EmailVerificationStatus:
    """Mark a verification token as used if it exists and is still valid."""
    token_hash = hash_token(token)
    stmt = select(EmailVerification).where(EmailVerification.token_hash == token_hash)
    record = db.scalars(stmt).first()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found.")
    if record.used_at is not None:
        return EmailVerificationStatus(status="already_used")
    if _as_utc(record.expires_at) < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired.")
    record.used_at = datetime.now(timezone.utc)
    team = _get_team_or_404(db, record.team_id)
    team.status = TeamStatus.ACTIVE
    db.add(record)
    db.add(team)
    db.commit()
    return EmailVerificationStatus(status="verified")


@router.get("/me", response_model=CaptainProfileRead)
def get_me(
    current: tuple[object, Team] = Depends(get_current_captain_session),
    db: Session = Depends(get_db),
) -> Team:
    """Return the captain-facing team profile."""
    _, team = current
    _ensure_verified(db, team.id)
    return _get_team_or_404(db, team.id)


@router.get("/members", response_model=list[MemberRead])
def list_members(
    current: tuple[object, Team] = Depends(get_current_captain_session),
    db: Session = Depends(get_db),
) -> list[Member]:
    """List members for a verified captain."""
    _, team = current
    _ensure_verified(db, team.id)
    stmt = select(Member).where(Member.team_id == team.id).order_by(Member.created_at, Member.id)
    return list(db.scalars(stmt).all())


@router.post("/members", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
def create_member(
    payload: MemberCreate,
    current: tuple[object, Team] = Depends(get_current_captain_session),
    db: Session = Depends(get_db),
) -> Member:
    """Create a member entry for a verified team captain."""
    _, team = current
    if payload.team_id != team.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Captain can only manage members for their own team.",
        )
    _get_team_or_404(db, payload.team_id)
    _ensure_verified(db, payload.team_id)
    member = Member(**payload.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member
