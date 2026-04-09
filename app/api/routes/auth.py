"""Authentication-related endpoints for the simplified LINE gate."""

from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.schemas.auth import LineEntryRequest, LineEntryResponse

router = APIRouter()
settings = get_settings()


def _is_allowed(line_user_id: str) -> bool:
    """Check whether the given LINE user id is allowed to access the site."""
    allowed_ids = settings.parsed_line_login_allowed_ids
    if not allowed_ids:
        return True
    return line_user_id in allowed_ids


@router.post("/line-entry", response_model=LineEntryResponse)
def line_entry(payload: LineEntryRequest) -> LineEntryResponse:
    """Validate a LINE user id for the static-site gate."""
    if not _is_allowed(payload.line_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="LINE user is not allowed to access this site.",
        )

    return LineEntryResponse(
        ok=True,
        message="LINE access granted.",
        line_user_id=payload.line_user_id,
        access_url="/",
    )
