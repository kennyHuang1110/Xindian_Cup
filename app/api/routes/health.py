"""Health-check endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return a simple liveness response."""
    return {"status": "ok", "service": "Xindian_Cup"}
