"""Schemas for member payloads."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MemberCreate(BaseModel):
    """Request payload to create a team member."""

    team_id: int
    name: str
    phone: str | None = None
    is_alumni: bool
    created_by: int | None = None


class MemberRead(MemberCreate):
    """Response payload for a member."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
