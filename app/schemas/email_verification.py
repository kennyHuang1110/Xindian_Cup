"""Schemas for email verification flows."""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class EmailVerificationRequest(BaseModel):
    """Request payload to issue a verification record."""

    team_id: int
    email: EmailStr


class EmailVerificationIssueResponse(BaseModel):
    """Response returned when a verification token is issued."""

    message: str
    expires_at: datetime


class EmailVerificationStatus(BaseModel):
    """Response for verification callback handling."""

    status: str
