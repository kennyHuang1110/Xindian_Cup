"""Schemas for auth and LINE entry endpoints."""

from pydantic import BaseModel, Field


class LineEntryRequest(BaseModel):
    """Incoming LINE entry payload."""

    line_user_id: str = Field(..., min_length=3, max_length=120)


class LineEntryResponse(BaseModel):
    """MVP response for a LINE entry request."""

    ok: bool
    message: str
    line_user_id: str
