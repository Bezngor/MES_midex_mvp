"""
API проверки готовности системы: маршруты и правила выбора РЦ для всех ГП.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.core.services.validation_service import get_routes_and_rules_validation

router = APIRouter(prefix="/api/v1/validation", tags=["validation"])


@router.get("/routes-and-rules")
async def validation_routes_and_rules(db: Session = Depends(get_db)):
    """
    Проверка: у всех ГП есть записи в маршрутах и в правилах выбора РЦ.

    Если ok=false, система не должна запускаться в работу (выпуск заказов блокируется).
    Пользователь видит список ГП и в каких «файлах» (маршруты / правила) для них нет записей.
    После довнесения данных можно снова вызвать этот endpoint («Проверить снова»).
    """
    data = get_routes_and_rules_validation(db)
    return {"success": True, "data": data}
