"""Schemas for auth and LINE entry endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class LineEntryRequest(BaseModel):
    """Incoming LINE entry payload."""

    team_id: int
    line_user_id: str = Field(..., min_length=3, max_length=120)


class LineEntryResponse(BaseModel):
    """MVP response for a LINE entry request."""

    ok: bool
    message: str
    team_id: int
    line_user_id: str
    session_token: str
    expires_at: datetime
