"""
Pydantic-схемы для спецификаций (BOM).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BOMCreate(BaseModel):
    """Схема создания строки спецификации."""

    parent_product_id: UUID = Field(..., description="UUID родительского продукта (FG или BULK).")
    child_product_id: UUID = Field(..., description="UUID дочернего продукта (компонент или сырьё).")
    quantity: Decimal = Field(..., gt=0, description="Количество компонента.")
    unit: str = Field(..., max_length=20, description="Единица измерения компонента.")
    sequence: Optional[int] = Field(
        default=None,
        description="Порядковый номер компонента в спецификации (опционально).",
    )


class BOMResponse(BaseModel):
    """Схема чтения строки спецификации. quantity допускает 0 (данные из БД)."""

    id: UUID
    parent_product_id: UUID
    child_product_id: UUID
    quantity: Decimal = Field(..., ge=0, description="Количество компонента (0 допустимо в БД).")
    unit: str = Field(..., max_length=20)
    sequence: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


