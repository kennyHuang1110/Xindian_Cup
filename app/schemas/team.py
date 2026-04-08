"""Schemas for team payloads."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.team import TeamStatus


class TeamBase(BaseModel):
    """Shared team fields."""

    team_name: str
    captain_name: str
    captain_email: EmailStr
    captain_phone: str | None = None
    captain_line_user_id: str | None = None
    status: TeamStatus = TeamStatus.PENDING


class TeamAdminCreate(BaseModel):
    """Admin request payload to create a team."""

    team_name: str
    captain_name: str
    captain_email: EmailStr
    captain_phone: str | None = None
    captain_line_user_id: str | None = None


class TeamAdminUpdate(BaseModel):
    """Admin request payload to update a team."""

    team_name: str | None = None
    captain_name: str | None = None
    captain_email: EmailStr | None = None
    captain_phone: str | None = None
    captain_line_user_id: str | None = None
    status: TeamStatus | None = None


class TeamRead(TeamBase):
    """Full team response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class PublicTeamRead(BaseModel):
    """Public listing for announcement pages."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    team_name: str
    captain_name: str
    status: TeamStatus
    created_at: datetime


class PublicTeamMemberRead(BaseModel):
    """Public member listing schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str | None
    is_alumni: bool
    created_at: datetime


class PublicTeamDetailRead(PublicTeamRead):
    """Public team schema including members."""

    members: list[PublicTeamMemberRead]


class CaptainProfileRead(TeamRead):
    """Captain-facing view of the team profile."""

    pass
