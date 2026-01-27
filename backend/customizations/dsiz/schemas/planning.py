"""
DSIZ Planning API Schemas.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import date
from uuid import UUID


class ManualBlock(BaseModel):
    """Ручная блокировка планирования."""
    work_center_id: str = Field(..., description="ID рабочего центра")
    shift_date: date = Field(..., description="Дата смены")
    shift_num: int = Field(..., ge=1, le=2, description="Номер смены (1 или 2)")
    reason: Optional[str] = Field(None, description="Причина блокировки")


class DsizPlanningRequest(BaseModel):
    """Схема запроса для запуска DSIZ планирования."""
    planning_date: date = Field(..., description="Дата начала планирования")
    horizon_days: int = Field(default=7, ge=1, le=30, description="Горизонт планирования в днях")
    manual_blocks: List[ManualBlock] = Field(default_factory=list, description="Ручные блокировки")
    workforce_state: Dict[str, Dict[str, int]] = Field(
        default_factory=dict,
        description="Состояние персонала по сменам: {'2026-01-27': {'OPERATOR': 5, 'PACKER': 2}}"
    )


class PlanningOperation(BaseModel):
    """Операция планирования (варка реактора)."""
    bulk_product_sku: str = Field(..., description="SKU Bulk продукта")
    quantity_kg: float = Field(..., description="Количество в кг")
    mode: str = Field(..., description="Режим реактора (CREAM_MODE или PASTE_MODE)")
    shift_date: date = Field(..., description="Дата смены")
    shift_num: int = Field(..., ge=1, le=2, description="Номер смены")
    reactor_slot: int = Field(..., ge=1, le=2, description="Слот реактора (1 или 2)")


class PlanningWarning(BaseModel):
    """Предупреждение при планировании."""
    level: str = Field(..., description="Уровень предупреждения (WARNING, ERROR)")
    message: str = Field(..., description="Текст предупреждения")
    context: Optional[Dict] = Field(None, description="Дополнительный контекст")


class DsizPlanningResponse(BaseModel):
    """Схема ответа для DSIZ планирования."""
    success: bool = Field(..., description="Успешность выполнения")
    plan_id: str = Field(..., description="ID плана планирования")
    planning_date: date = Field(..., description="Дата планирования")
    horizon_days: int = Field(..., description="Горизонт планирования")
    operations: List[PlanningOperation] = Field(default_factory=list, description="Список операций планирования")
    warnings: List[PlanningWarning] = Field(default_factory=list, description="Список предупреждений")
    summary: Dict = Field(default_factory=dict, description="Сводка планирования")
