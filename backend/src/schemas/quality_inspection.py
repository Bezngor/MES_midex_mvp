"""
Pydantic schemas for QualityInspection.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import Any

from backend.src.models.enums import QualityStatus


class QualityInspectionBase(BaseModel):
    """Base schema for QualityInspection."""

    task_id: UUID
    inspector_id: str
    measurements: dict[str, Any] | None = None
    notes: str | None = None


class QualityInspectionCreate(QualityInspectionBase):
    """Schema for creating a QualityInspection."""

    inspection_timestamp: datetime | None = None
    status: QualityStatus = QualityStatus.PENDING


class QualityInspectionRead(QualityInspectionBase):
    """Schema for reading a QualityInspection."""

    id: UUID
    inspection_timestamp: datetime
    status: QualityStatus

    model_config = ConfigDict(from_attributes=True)


class QualityInspectionUpdate(BaseModel):
    """Schema for updating a QualityInspection."""

    status: QualityStatus | None = None
    measurements: dict[str, Any] | None = None
    notes: str | None = None
