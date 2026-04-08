"""Authentication-related endpoints."""

from fastapi import APIRouter

from app.schemas.auth import LineEntryRequest, LineEntryResponse

router = APIRouter()


@router.post("/line-entry", response_model=LineEntryResponse)
def line_entry(payload: LineEntryRequest) -> LineEntryResponse:
    """Placeholder for LINE entry validation and session bootstrap."""
    return LineEntryResponse(
        ok=True,
        message="LINE entry accepted for MVP skeleton.",
        line_user_id=payload.line_user_id,
    )
