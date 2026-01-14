"""
Pydantic-схемы для ManufacturingOrder.
"""

from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

from backend.src.models.enums import OrderStatus, OrderPriority, OrderType
from backend.src.schemas.production_task import ProductionTaskRead


class ManufacturingOrderBase(BaseModel):
    """Базовая схема для ManufacturingOrder."""

    order_number: str
    product_id: str
    quantity: Decimal = Field(gt=0, description="Количество должно быть больше 0.")
    due_date: datetime
    order_type: OrderType = Field(
        default=OrderType.CUSTOMER,
        description="Тип заказа (CUSTOMER или INTERNAL_BULK).",
    )
    priority: Optional[OrderPriority] = Field(
        default=None,
        description="Приоритет заказа (URGENT, HIGH, NORMAL, LOW).",
    )
    parent_order_id: Optional[UUID] = Field(
        default=None,
        description="Родительский заказ (для внутренних bulk-заказов).",
    )
    source_order_ids: Optional[list[UUID]] = Field(
        default=None,
        description="Список UUID заказов, консолидированных в данный.",
    )
    is_consolidated: bool = Field(
        default=False,
        description="Флаг, что заказ является консолидированным.",
    )


class ManufacturingOrderCreate(ManufacturingOrderBase):
    """Схема создания ManufacturingOrder."""


class ManufacturingOrderRead(ManufacturingOrderBase):
    """Схема чтения ManufacturingOrder."""

    id: UUID
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ManufacturingOrderWithTasksRead(ManufacturingOrderRead):
    """Схема чтения ManufacturingOrder с задачами."""

    production_tasks: List[ProductionTaskRead] = []

    model_config = ConfigDict(from_attributes=True)


class ManufacturingOrderUpdate(BaseModel):
    """Схема обновления ManufacturingOrder."""

    status: OrderStatus | None = None
    quantity: Decimal | None = Field(None, gt=0)
    priority: Optional[OrderPriority] = None
    order_type: Optional[OrderType] = None
    parent_order_id: Optional[UUID] = None
    source_order_ids: Optional[list[UUID]] = None
    is_consolidated: Optional[bool] = None
