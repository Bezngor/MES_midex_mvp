"""
SQLAlchemy-модель для ManufacturingOrder.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, Enum, Index, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from backend.src.db.session import Base
from backend.src.models.enums import OrderStatus


class ManufacturingOrder(Base):
    """Модель производственного заказа."""

    __tablename__ = "manufacturing_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    order_number = Column(String, unique=True, nullable=False, index=True)
    product_id = Column(String, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(OrderStatus, native_enum=False), nullable=False, default=OrderStatus.PLANNED)
    due_date = Column(DateTime(timezone=True), nullable=False)

    # Расширения для process manufacturing
    order_type = Column(String(50), nullable=False, default="CUSTOMER", index=True)
    priority = Column(String(50), nullable=True, index=True)
    parent_order_id = Column(UUID(as_uuid=True), ForeignKey("manufacturing_orders.id"), nullable=True, index=True)
    source_order_ids = Column(JSONB, nullable=True)
    is_consolidated = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    production_tasks = relationship("ProductionTask", back_populates="manufacturing_order", cascade="all, delete-orphan")
    batches = relationship("Batch", back_populates="parent_order")
    parent_order = relationship(
        "ManufacturingOrder",
        remote_side=[id],
        foreign_keys=[parent_order_id],
        backref="dependent_orders",
    )

    # Indexes
    __table_args__ = (
        Index("idx_manufacturing_orders_status", "status"),
        Index("idx_manufacturing_orders_due_date", "due_date"),
        Index("idx_orders_type", "order_type"),
        Index("idx_orders_priority", "priority"),
        Index("idx_orders_parent", "parent_order_id"),
    )

    def __repr__(self) -> str:
        """Текстовое представление производственного заказа."""
        return f"<ManufacturingOrder(id={self.id}, order_number={self.order_number}, status={self.status})>"
