"""
Pydantic schemas for ProductionTask.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from backend.src.models.enums import TaskStatus


class ProductionTaskBase(BaseModel):
    """Base schema for ProductionTask."""

    order_id: UUID
    operation_id: UUID
    work_center_id: UUID
    assigned_to: str | None = None


class ProductionTaskRead(ProductionTaskBase):
    """Schema for reading a ProductionTask."""

    id: UUID
    status: TaskStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductionTaskUpdate(BaseModel):
    """Schema for updating a ProductionTask."""

    status: TaskStatus | None = None
    assigned_to: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class TaskStartPayload(BaseModel):
    """Payload schema for starting a task."""

    operator_id: str | None = Field(None, description="ID of the operator starting the task")


class TaskCompletePayload(BaseModel):
    """Payload schema for completing a task."""

    notes: str | None = Field(None, description="Optional completion notes")


class TaskFailPayload(BaseModel):
    """Payload schema for failing a task."""

    reason: str = Field(..., description="Reason for task failure")
