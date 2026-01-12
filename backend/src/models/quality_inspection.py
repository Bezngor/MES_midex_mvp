"""
SQLAlchemy model for QualityInspection.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from backend.src.db.session import Base
from backend.src.models.enums import QualityStatus


class QualityInspection(Base):
    """Quality inspection model."""

    __tablename__ = "quality_inspections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("production_tasks.id", ondelete="CASCADE"), nullable=False)
    inspector_id = Column(String, nullable=False)
    inspection_timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    measurements = Column(JSONB, nullable=True)
    status = Column(Enum(QualityStatus, native_enum=False), nullable=False, default=QualityStatus.PENDING)
    notes = Column(String, nullable=True)

    # Relationships
    production_task = relationship("ProductionTask", back_populates="quality_inspections")

    # Indexes
    __table_args__ = (
        Index("idx_quality_inspections_task_id", "task_id"),
    )

    def __repr__(self):
        return f"<QualityInspection(id={self.id}, task_id={self.task_id}, status={self.status})>"
