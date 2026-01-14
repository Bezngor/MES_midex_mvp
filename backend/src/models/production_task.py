"""
SQLAlchemy-модель для ProductionTask.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Index, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.db.session import Base
from backend.src.models.enums import TaskStatus


class ProductionTask(Base):
    """Модель производственной задачи."""

    __tablename__ = "production_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("manufacturing_orders.id", ondelete="CASCADE"), nullable=False)
    operation_id = Column(UUID(as_uuid=True), ForeignKey("route_operations.id"), nullable=False)
    work_center_id = Column(UUID(as_uuid=True), ForeignKey("work_centers.id"), nullable=False)
    status = Column(Enum(TaskStatus, native_enum=False), nullable=False, default=TaskStatus.QUEUED)
    assigned_to = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Расширения для process manufacturing
    batch_id = Column(UUID(as_uuid=True), ForeignKey("batches.id"), nullable=True, index=True)
    quantity_kg = Column(Numeric(10, 2), nullable=True)
    quantity_pcs = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    manufacturing_order = relationship("ManufacturingOrder", back_populates="production_tasks")
    route_operation = relationship("RouteOperation", back_populates="production_tasks")
    work_center = relationship("WorkCenter", back_populates="production_tasks")
    batch = relationship("Batch", back_populates="tasks")
    genealogy_records = relationship("GenealogyRecord", back_populates="production_task", cascade="all, delete-orphan")
    quality_inspections = relationship("QualityInspection", back_populates="production_task", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_production_tasks_status", "status"),
        Index("idx_production_tasks_work_center_id", "work_center_id"),
        Index("idx_production_tasks_task_id", "id"),  # For genealogy and quality lookups
    )

    def __repr__(self) -> str:
        """Текстовое представление производственной задачи."""
        return f"<ProductionTask(id={self.id}, status={self.status}, work_center_id={self.work_center_id})>"
