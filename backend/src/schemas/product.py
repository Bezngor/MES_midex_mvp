"""
Pydantic-схемы для продуктов.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.src.models.enums import ProductType


class ProductCreate(BaseModel):
    """Схема создания продукта."""

    product_code: str = Field(..., max_length=100, description="Уникальный код продукта (SKU).")
    product_name: str = Field(..., max_length=255, description="Наименование продукта.")
    product_type: ProductType = Field(..., description="Тип продукта.")
    unit_of_measure: str = Field(..., max_length=20, description="Единица измерения (шт, кг и т.д.).")

    # Для BULK-продуктов
    min_batch_size_kg: Optional[Decimal] = Field(
        default=None,
        description="Минимальный размер батча, кг (только для BULK).",
    )
    batch_size_step_kg: Optional[Decimal] = Field(
        default=None,
        description="Шаг размера батча, кг (только для BULK).",
    )
    shelf_life_days: Optional[int] = Field(
        default=None,
        description="Срок годности в днях (для BULK и при необходимости ГП).",
    )


class ProductUpdate(BaseModel):
    """Схема обновления продукта."""

    product_name: Optional[str] = Field(default=None, max_length=255)
    product_type: Optional[ProductType] = None
    unit_of_measure: Optional[str] = Field(default=None, max_length=20)
    min_batch_size_kg: Optional[Decimal] = None
    batch_size_step_kg: Optional[Decimal] = None
    shelf_life_days: Optional[int] = None


class ProductResponse(ProductCreate):
    """Схема чтения продукта."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


