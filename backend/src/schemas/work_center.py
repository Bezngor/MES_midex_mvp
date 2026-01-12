"""
Pydantic schemas for WorkCenter.
"""

from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

from backend.src.models.enums import WorkCenterStatus


class WorkCenterBase(BaseModel):
    """Base schema for WorkCenter."""

    name: str
    resource_type: str
    capacity_units_per_hour: Decimal = Field(gt=0, description="Capacity must be greater than 0")


class WorkCenterCreate(WorkCenterBase):
    """Schema for creating a WorkCenter."""

    status: WorkCenterStatus = WorkCenterStatus.AVAILABLE


class WorkCenterRead(WorkCenterBase):
    """Schema for reading a WorkCenter."""

    id: UUID
    status: WorkCenterStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkCenterUpdate(BaseModel):
    """Schema for updating a WorkCenter."""

    name: str | None = None
    status: WorkCenterStatus | None = None
    capacity_units_per_hour: Decimal | None = Field(None, gt=0)
