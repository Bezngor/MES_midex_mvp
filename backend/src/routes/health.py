"""
Health check endpoint.
"""

from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns API status and timestamp.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "mes-api",
    }
