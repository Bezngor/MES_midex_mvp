"""
Pydantic-схемы для WorkCenter.
"""

from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List

from backend.core.models.enums import WorkCenterStatus


class WorkCenterBase(BaseModel):
    """Базовая схема для WorkCenter."""

    name: str
    resource_type: str
    capacity_units_per_hour: Decimal = Field(
        gt=0,
        description="Производительность в единицах в час должна быть больше 0.",
    )
    batch_capacity_kg: Optional[Decimal] = Field(
        default=None,
        description="Ёмкость реактора/миксера в кг.",
    )
    cycles_per_shift: Optional[int] = Field(
        default=None,
        description="Количество циклов за смену.",
    )
    exclusive_products: Optional[List[UUID]] = Field(
        default=None,
        description="Список UUID продуктов, которые нельзя производить параллельно.",
    )
    parallel_capacity: Optional[int] = Field(
        default=1,
        description="Количество параллельных задач, которые может обрабатывать РЦ.",
    )


class WorkCenterCreate(WorkCenterBase):
    """Схема создания WorkCenter."""

    status: WorkCenterStatus = WorkCenterStatus.AVAILABLE


class WorkCenterRead(WorkCenterBase):
    """Схема чтения WorkCenter."""

    id: UUID
    status: WorkCenterStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkCenterUpdate(BaseModel):
    """Схема обновления WorkCenter."""

    name: str | None = None
    status: WorkCenterStatus | None = None
    capacity_units_per_hour: Decimal | None = Field(None, gt=0)
    batch_capacity_kg: Optional[Decimal] = None
    cycles_per_shift: Optional[int] = None
    exclusive_products: Optional[List[UUID]] = None
    parallel_capacity: Optional[int] = None
