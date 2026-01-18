"""
Pydantic schemas for ManufacturingRoute.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import List

from backend.core.schemas.route_operation import RouteOperationRead


class ManufacturingRouteBase(BaseModel):
    """Base schema for ManufacturingRoute."""

    product_id: str
    route_name: str
    description: str | None = None


class ManufacturingRouteCreate(ManufacturingRouteBase):
    """Schema for creating a ManufacturingRoute."""

    pass


class ManufacturingRouteRead(ManufacturingRouteBase):
    """Schema for reading a ManufacturingRoute."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ManufacturingRouteWithOperationsRead(ManufacturingRouteRead):
    """Schema for reading a ManufacturingRoute with associated RouteOperations."""

    route_operations: List[RouteOperationRead] = []

    model_config = ConfigDict(from_attributes=True)
