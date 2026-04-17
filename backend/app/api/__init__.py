from fastapi import APIRouter

from .mvp import router as mvp_router

router = APIRouter()
router.include_router(mvp_router, prefix="/api/mvp", tags=["mvp"])

__all__ = ["router"]
