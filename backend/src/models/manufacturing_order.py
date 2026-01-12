"""
SQLAlchemy model for ManufacturingOrder.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.db.session import Base
from backend.src.models.enums import OrderStatus


class ManufacturingOrder(Base):
    """Manufacturing order model."""

    __tablename__ = "manufacturing_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    order_number = Column(String, unique=True, nullable=False, index=True)
    product_id = Column(String, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(OrderStatus, native_enum=False), nullable=False, default=OrderStatus.PLANNED)
    due_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    production_tasks = relationship("ProductionTask", back_populates="manufacturing_order", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_manufacturing_orders_status", "status"),
        Index("idx_manufacturing_orders_due_date", "due_date"),
    )

    def __repr__(self):
        return f"<ManufacturingOrder(id={self.id}, order_number={self.order_number}, status={self.status})>"
