"""
Health check endpoint for Docker healthcheck.
"""

import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.src.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint для Docker healthcheck.
    Проверяет доступность API и подключение к БД.
    """
    try:
        # Проверка подключения к БД
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "version": "2.1.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "version": "2.1.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "database": "disconnected",
            "error": str(e)
        }
