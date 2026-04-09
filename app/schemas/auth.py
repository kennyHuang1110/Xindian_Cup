"""Schemas for the simplified LINE gate."""

from pydantic import BaseModel, Field


class LineEntryRequest(BaseModel):
    """Incoming LINE gate payload."""

    line_user_id: str = Field(..., min_length=3, max_length=120)


class LineEntryResponse(BaseModel):
    """Response for the simplified LINE gate."""

    ok: bool
    message: str
    line_user_id: str
    access_url: str
