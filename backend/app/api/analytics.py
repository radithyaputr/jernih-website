from fastapi import APIRouter
from app.core.ai import get_analytics

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("")
async def analytics():
    return get_analytics()
