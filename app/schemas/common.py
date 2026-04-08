"""Shared response schemas."""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Generic message response payload."""

    message: str
