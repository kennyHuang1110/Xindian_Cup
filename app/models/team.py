"""Team model definitions."""

from enum import Enum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class TeamStatus(str, Enum):
    """Allowed team lifecycle statuses."""

    PENDING = "pending"
    ACTIVE = "active"
    DISABLED = "disabled"


class Team(TimestampMixin, Base):
    """Registered team with captain contact details."""

    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    team_name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    captain_name: Mapped[str] = mapped_column(String(120), nullable=False)
    captain_email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    captain_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    captain_line_user_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[TeamStatus] = mapped_column(
        SqlEnum(TeamStatus, name="team_status"),
        default=TeamStatus.PENDING,
        nullable=False,
    )

    members = relationship("Member", back_populates="team", cascade="all, delete-orphan")
    email_verifications = relationship(
        "EmailVerification", back_populates="team", cascade="all, delete-orphan"
    )
    sessions = relationship("Session", back_populates="team", cascade="all, delete-orphan")
