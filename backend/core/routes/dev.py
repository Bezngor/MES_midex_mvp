"""
Эндпоинты только для тестовой/разработческой среды.

В production (ENVIRONMENT=production) эти эндпоинты возвращают 403.
"""

import os
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/v1/dev", tags=["Dev (test only)"])


def _is_test_env() -> bool:
    env = os.getenv("ENVIRONMENT", "development").lower()
    return env in ("test", "development", "dev")


@router.post("/reset-all-tables")
async def reset_all_tables():
    """
    Очистить все таблицы БД (только для тестовой версии).

    В production возвращает 403. После вызова нужно заново выполнить
    prepare_test_env (или миграции + seed + load_routes_from_csv).
    """
    if not _is_test_env():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только при ENVIRONMENT=test или development",
        )
    from backend.src.db.clear_all_tables import clear_all_tables

    clear_all_tables()
    return {
        "success": True,
        "message": "Все таблицы очищены. Запустите prepare_test_env для повторной загрузки данных.",
    }
