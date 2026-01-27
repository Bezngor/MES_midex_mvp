"""
Pydantic-схемы для ProductionTask.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal

from backend.core.models.enums import TaskStatus


class ProductionTaskBase(BaseModel):
    """Базовая схема для ProductionTask."""

    order_id: UUID
    operation_id: UUID
    work_center_id: UUID
    assigned_to: str | None = None
    batch_id: UUID | None = None
    quantity_kg: Decimal | None = Field(
        default=None,
        description="Количество в кг (для процессных операций).",
    )
    quantity_pcs: int | None = Field(
        default=None,
        description="Количество в штуках (для дискретных операций).",
    )


class ProductionTaskRead(ProductionTaskBase):
    """Схема чтения ProductionTask."""

    id: UUID
    status: TaskStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductionTaskUpdate(BaseModel):
    """Схема обновления ProductionTask."""

    status: TaskStatus | None = None
    assigned_to: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    batch_id: UUID | None = None
    quantity_kg: Decimal | None = None
    quantity_pcs: int | None = None


class TaskStartPayload(BaseModel):
    """Схема полезной нагрузки для старта задачи."""

    operator_id: str | None = Field(None, description="ID of the operator starting the task")


class TaskCompletePayload(BaseModel):
    """Схема полезной нагрузки для завершения задачи."""

    notes: str | None = Field(None, description="Optional completion notes")


class TaskFailPayload(BaseModel):
    """Схема полезной нагрузки для провала задачи."""

    reason: str = Field(..., description="Reason for task failure")
