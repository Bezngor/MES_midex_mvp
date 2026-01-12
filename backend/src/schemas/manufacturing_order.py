"""
Pydantic schemas for ManufacturingOrder.
"""

from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from typing import List

from backend.src.models.enums import OrderStatus
from backend.src.schemas.production_task import ProductionTaskRead


class ManufacturingOrderBase(BaseModel):
    """Base schema for ManufacturingOrder."""

    order_number: str
    product_id: str
    quantity: Decimal = Field(gt=0, description="Quantity must be greater than 0")
    due_date: datetime


class ManufacturingOrderCreate(ManufacturingOrderBase):
    """Schema for creating a ManufacturingOrder."""

    pass


class ManufacturingOrderRead(ManufacturingOrderBase):
    """Schema for reading a ManufacturingOrder."""

    id: UUID
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ManufacturingOrderWithTasksRead(ManufacturingOrderRead):
    """Schema for reading a ManufacturingOrder with associated ProductionTasks."""

    production_tasks: List[ProductionTaskRead] = []

    model_config = ConfigDict(from_attributes=True)


class ManufacturingOrderUpdate(BaseModel):
    """Schema for updating a ManufacturingOrder."""

    status: OrderStatus | None = None
    quantity: Decimal | None = Field(None, gt=0)
