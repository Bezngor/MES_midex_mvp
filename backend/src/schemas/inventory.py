"""
Pydantic-схемы для остатков (InventoryBalance).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.src.models.enums import ProductStatus


class InventoryAdjust(BaseModel):
    """Схема корректировки остатка."""

    product_id: UUID = Field(..., description="UUID продукта.")
    location: str = Field(..., max_length=100, description="Код локации (WAREHOUSE, CUB_1 и т.д.).")
    quantity: Optional[Decimal] = Field(
        default=None,
        ge=0,
        description="Абсолютное значение количества. Если указано, устанавливает это значение. Взаимоисключающе с quantity_delta.",
    )
    quantity_delta: Optional[Decimal] = Field(
        default=None,
        description="Изменение количества (может быть отрицательным). Если указано, добавляет к текущему значению. Взаимоисключающе с quantity.",
    )
    unit: str = Field(..., max_length=20, description="Единица измерения.")
    product_status: ProductStatus = Field(
        default=ProductStatus.FINISHED,
        description="Статус продукта (FINISHED или SEMI_FINISHED).",
    )
    production_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    reserved_quantity: Optional[Decimal] = Field(
        default=None,
        ge=0,
        description="Абсолютное значение резерва. Если указано, устанавливает это значение.",
    )
    reserved_delta: Optional[Decimal] = Field(
        default=None,
        description="Изменение резерва (может быть отрицательным). Если указано, добавляет к текущему значению.",
    )

    @model_validator(mode='after')
    def validate_quantity_fields(self) -> 'InventoryAdjust':
        """Валидация: quantity и quantity_delta не могут быть указаны одновременно."""
        if self.quantity is not None and self.quantity_delta is not None:
            raise ValueError("Нельзя указывать одновременно quantity и quantity_delta. Используйте одно из полей.")
        if self.quantity is None and self.quantity_delta is None:
            raise ValueError("Необходимо указать либо quantity, либо quantity_delta.")
        return self


class InventoryResponse(BaseModel):
    """Схема чтения остатка по продукту и локации."""

    id: UUID
    product_id: UUID
    location: str
    quantity: Decimal
    unit: str
    product_status: ProductStatus
    production_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    reserved_quantity: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


