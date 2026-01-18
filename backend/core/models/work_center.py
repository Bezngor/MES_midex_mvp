"""
SQLAlchemy model for WorkCenter.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, Enum, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.db.session import Base
from backend.core.models.enums import WorkCenterStatus


class WorkCenter(Base):
    """Модель рабочего центра."""

    __tablename__ = "work_centers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    status = Column(Enum(WorkCenterStatus, native_enum=False), nullable=False, default=WorkCenterStatus.AVAILABLE)
    capacity_units_per_hour = Column(Numeric(10, 2), nullable=False)

    # Расширения для process manufacturing
    batch_capacity_kg = Column(Numeric(10, 2), nullable=True)
    cycles_per_shift = Column(Integer, nullable=True)
    exclusive_products = Column(JSONB, nullable=True)
    parallel_capacity = Column(Integer, nullable=False, default=1)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    route_operations = relationship("RouteOperation", back_populates="work_center")
    production_tasks = relationship("ProductionTask", back_populates="work_center")
    capacities = relationship("WorkCenterCapacity", back_populates="work_center", cascade="all, delete-orphan")
    batches = relationship("Batch", back_populates="work_center")

    def __repr__(self) -> str:
        """Текстовое представление рабочего центра."""
        return f"<WorkCenter(id={self.id}, name={self.name}, status={self.status})>"
