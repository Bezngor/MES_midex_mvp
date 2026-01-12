"""
SQLAlchemy model for WorkCenter.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.db.session import Base
from backend.src.models.enums import WorkCenterStatus


class WorkCenter(Base):
    """Work center model."""

    __tablename__ = "work_centers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    status = Column(Enum(WorkCenterStatus, native_enum=False), nullable=False, default=WorkCenterStatus.AVAILABLE)
    capacity_units_per_hour = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    route_operations = relationship("RouteOperation", back_populates="work_center")
    production_tasks = relationship("ProductionTask", back_populates="work_center")

    def __repr__(self):
        return f"<WorkCenter(id={self.id}, name={self.name}, status={self.status})>"
