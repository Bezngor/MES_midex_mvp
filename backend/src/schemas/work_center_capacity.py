"""
Pydantic-схемы для мощностей рабочих центров по продукту.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CapacityCreate(BaseModel):
    """Схема создания записи мощности рабочего центра по продукту."""

    work_center_id: UUID = Field(..., description="UUID рабочего центра.")
    product_id: UUID = Field(..., description="UUID продукта.")
    capacity_per_shift: Decimal = Field(
        ...,
        gt=0,
        description="Мощность за смену (например, кг/смену или шт/смену).",
    )
    unit: str = Field(..., max_length=20, description="Единица мощности (PCS_PER_SHIFT, KG_PER_SHIFT и т.д.).")


class CapacityResponse(CapacityCreate):
    """Схема чтения мощности рабочего центра по продукту."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


