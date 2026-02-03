"""
API роутер для стратегического планирования производства.
"""

from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.core.services.strategic_planning_service import StrategicPlanningService

router = APIRouter(prefix="/api/v1/strategic-planning", tags=["strategic-planning"])


class RecalculatePlanRequest(BaseModel):
    """Запрос на пересчёт плана производства."""

    order_ids: List[str] = Field(..., description="Список ID заказов, отмеченных 'Принять'")


@router.post(
    "/recalculate-plan",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Пересчитать план производства",
    description="Пересчитывает план производства для принятых заказов согласно алгоритму стратегического планирования",
)
async def recalculate_plan(
    request: RecalculatePlanRequest,
    db: Session = Depends(get_db),
):
    """
    Пересчитать план производства для принятых заказов.

    Args:
        request: Запрос со списком ID заказов

    Returns:
        Результаты планирования:
        - reserved_orders: Заказы с успешно зарезервированными компонентами
        - failed_orders: Заказы с ошибками резервирования (что и сколько не хватает)
        - planned_operations: Запланированные операции производства
    """
    try:
        # Конвертируем строки в UUID
        accepted_order_ids = [UUID(order_id) for order_id in request.order_ids]
    except (ValueError, AttributeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректный формат ID заказа: {str(e)}",
        )

    if not accepted_order_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не указаны заказы для планирования",
        )

    service = StrategicPlanningService(db)

    try:
        result = service.recalculate_plan(accepted_order_ids)
        return {
            "success": True,
            "data": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при пересчёте плана: {str(e)}",
        )
