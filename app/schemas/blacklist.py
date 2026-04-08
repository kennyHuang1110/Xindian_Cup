"""Schemas for blacklist payloads."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BlacklistCreate(BaseModel):
    """Request payload to create a blacklist entry."""

    type: str
    value: str
    reason: str | None = None
    is_active: bool = True


class BlacklistRead(BlacklistCreate):
    """Response payload for blacklist entries."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
