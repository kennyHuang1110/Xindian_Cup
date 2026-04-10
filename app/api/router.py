"""Top-level API router registration."""

from fastapi import APIRouter

from app.api.routes import health, public

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(public.router, prefix="/api/public", tags=["public"])
