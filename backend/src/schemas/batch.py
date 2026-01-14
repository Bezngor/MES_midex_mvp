"""
Pydantic-схемы для батчей (bulk-партий).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.src.models.enums import BatchStatus


class BatchCreate(BaseModel):
    """Схема создания батча."""

    batch_number: Optional[str] = Field(default=None, max_length=100, description="Уникальный номер батча. Если не указан, будет сгенерирован автоматически.")
    product_id: UUID = Field(..., description="UUID продукта (обычно BULK).")
    quantity_kg: Decimal = Field(..., gt=0, description="Плановый объём батча в кг.")
    status: BatchStatus = Field(default=BatchStatus.PLANNED, description="Статус батча.")

    work_center_id: Optional[UUID] = Field(default=None, description="UUID реактора/миксера.")
    operator_id: Optional[str] = Field(default=None, max_length=100, description="Идентификатор оператора.")
    planned_start: Optional[datetime] = Field(default=None, description="Плановое время старта.")
    storage_location_id: Optional[UUID] = Field(default=None, description="UUID локации хранения.")
    parent_order_id: Optional[UUID] = Field(
        default=None,
        description="UUID родительского производственного заказа.",
    )


class BatchUpdate(BaseModel):
    """Схема частичного обновления батча."""

    status: Optional[BatchStatus] = None
    work_center_id: Optional[UUID] = None
    operator_id: Optional[str] = None
    planned_start: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class BatchResponse(BatchCreate):
    """Схема чтения батча."""

    id: UUID
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


