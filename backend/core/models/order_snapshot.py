"""
SQLAlchemy-модель для снимков состояния производственных заказов.

Используется для отслеживания изменений заказов и выявления новых/изменённых ЗП
в рамках бизнес-процесса "Блок обновления данных".
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Index, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from backend.src.db.session import Base


class OrderSnapshot(Base):
    """Модель снимка состояния производственного заказа."""

    __tablename__ = "order_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("manufacturing_orders.id", ondelete="SET NULL"), nullable=True, index=True)
    order_number = Column(String, nullable=False, index=True)
    
    # Состояние заказа на момент снимка
    product_id = Column(String, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    order_type = Column(String(50), nullable=False)
    priority = Column(String(50), nullable=True)
    source_status = Column(String(50), nullable=True)
    parent_order_id = Column(UUID(as_uuid=True), nullable=True)
    source_order_ids = Column(JSONB, nullable=True)
    is_consolidated = Column(Boolean, nullable=False, default=False)
    
    # Метаданные снимка
    snapshot_date = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    snapshot_type = Column(String(50), nullable=False, default="MANUAL", index=True)  # MANUAL, AUTO, SYNC
    notes = Column(Text, nullable=True)
    
    # Полный JSON снимка для детального сравнения
    full_snapshot = Column(JSONB, nullable=True)

    # Relationships
    order = relationship("ManufacturingOrder", backref="snapshots")

    # Indexes
    __table_args__ = (
        Index("idx_order_snapshots_order_id", "order_id"),
        Index("idx_order_snapshots_order_number", "order_number"),
        Index("idx_order_snapshots_order_number_type", "order_number", "order_type"),  # Для поиска по бизнес-ключу
        Index("idx_order_snapshots_date", "snapshot_date"),
        Index("idx_order_snapshots_type", "snapshot_type"),
        Index("idx_order_snapshots_order_date", "order_id", "snapshot_date"),
    )

    def __repr__(self) -> str:
        """Текстовое представление снимка."""
        return f"<OrderSnapshot(id={self.id}, order_number={self.order_number}, snapshot_date={self.snapshot_date})>"
