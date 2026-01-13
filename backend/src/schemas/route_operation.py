"""
Pydantic schemas for RouteOperation.
"""

from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class RouteOperationBase(BaseModel):
    """Base schema for RouteOperation."""

    route_id: UUID
    operation_sequence: int = Field(ge=1, description="Sequence must be >= 1")
    operation_name: str
    work_center_id: UUID
    estimated_duration_minutes: int = Field(gt=0, description="Duration must be greater than 0")


class RouteOperationCreate(RouteOperationBase):
    """Schema for creating a RouteOperation."""

    pass


class RouteOperationRead(RouteOperationBase):
    """Schema for reading a RouteOperation."""

    id: UUID

    model_config = ConfigDict(from_attributes=True)


class RouteOperationUpdate(BaseModel):
    """Schema for updating a RouteOperation."""

    operation_sequence: int | None = Field(None, ge=1)
    operation_name: str | None = None
    work_center_id: UUID | None = None
    estimated_duration_minutes: int | None = Field(None, gt=0)
