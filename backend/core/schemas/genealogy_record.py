"""
Pydantic schemas for GenealogyRecord.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class GenealogyRecordBase(BaseModel):
    """Base schema for GenealogyRecord."""

    task_id: UUID
    operator_id: str
    event_type: str
    notes: str | None = None


class GenealogyRecordCreate(GenealogyRecordBase):
    """Schema for creating a GenealogyRecord."""

    timestamp: datetime | None = None


class GenealogyRecordRead(GenealogyRecordBase):
    """Schema for reading a GenealogyRecord."""

    id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
