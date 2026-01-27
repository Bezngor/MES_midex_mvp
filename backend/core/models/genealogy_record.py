"""
SQLAlchemy model for GenealogyRecord.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.db.session import Base


class GenealogyRecord(Base):
    """Genealogy record model (immutable audit trail)."""

    __tablename__ = "genealogy_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("production_tasks.id", ondelete="CASCADE"), nullable=False)
    operator_id = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    notes = Column(String, nullable=True)

    # Relationships
    production_task = relationship("ProductionTask", back_populates="genealogy_records")

    # Indexes
    __table_args__ = (
        Index("idx_genealogy_records_task_id", "task_id"),
    )

    def __repr__(self):
        return f"<GenealogyRecord(id={self.id}, task_id={self.task_id}, event_type={self.event_type})>"
