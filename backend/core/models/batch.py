"""
SQLAlchemy-модель производственного батча (bulk-партия).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from backend.src.db.session import Base
from backend.core.models.enums import BatchStatus


class Batch(Base):
    """Модель производственного батча (bulk-партия)."""

    __tablename__ = "batches"

    id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    batch_number: Mapped[str] = Column(String(100), unique=True, nullable=False, index=True)
    product_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )
    quantity_kg: Mapped[float] = Column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = Column(String(50), nullable=False, index=True)

    work_center_id: Mapped[uuid.UUID | None] = Column(
        UUID(as_uuid=True),
        ForeignKey("work_centers.id", ondelete="SET NULL"),
        nullable=True,
    )
    operator_id: Mapped[str | None] = Column(String(100), nullable=True)

    planned_start: Mapped[datetime | None] = Column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[datetime | None] = Column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = Column(DateTime(timezone=True), nullable=True)
    posted_to_inventory_at: Mapped[datetime | None] = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Время учёта партии в остатках; null — ещё не учтено.",
    )

    storage_location_id: Mapped[uuid.UUID | None] = Column(UUID(as_uuid=True), nullable=True)
    parent_order_id: Mapped[uuid.UUID | None] = Column(
        UUID(as_uuid=True),
        ForeignKey("manufacturing_orders.id"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Связи
    product: Mapped["Product"] = relationship("Product", back_populates="batches")
    work_center: Mapped["WorkCenter"] = relationship("WorkCenter", back_populates="batches")
    parent_order: Mapped["ManufacturingOrder"] = relationship(
        "ManufacturingOrder",
        back_populates="batches",
    )
    tasks: Mapped[List["ProductionTask"]] = relationship(
        "ProductionTask",
        back_populates="batch",
    )

    def __repr__(self) -> str:
        """Текстовое представление батча."""
        return f"<Batch(id={self.id}, number={self.batch_number}, status={self.status})>"

