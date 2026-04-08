"""Top-level API router registration."""

from fastapi import APIRouter

from app.api.routes import admin, auth, captain, health, public

api_router = APIRouter()
api_router.include_router(public.page_router)
api_router.include_router(health.router, tags=["health"])
api_router.include_router(public.router, prefix="/api/public", tags=["public"])
api_router.include_router(auth.router, prefix="/api/auth", tags=["auth"])
api_router.include_router(captain.router, prefix="/api/captain", tags=["captain"])
api_router.include_router(admin.router, prefix="/api/admin", tags=["admin"])
