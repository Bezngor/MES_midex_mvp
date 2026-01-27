"""
SQLAlchemy-модель мощностей рабочего центра по продукту.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from backend.src.db.session import Base


class WorkCenterCapacity(Base):
    """Модель мощности рабочего центра по конкретному продукту."""

    __tablename__ = "work_center_capacities"

    id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    work_center_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("work_centers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    capacity_per_shift: Mapped[float] = Column(Numeric(10, 2), nullable=False)
    unit: Mapped[str] = Column(String(20), nullable=False)

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

    __table_args__ = (
        UniqueConstraint("work_center_id", "product_id", name="uq_wc_product"),
    )

    # Связи
    work_center: Mapped["WorkCenter"] = relationship(
        "WorkCenter",
        back_populates="capacities",
    )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="work_center_capacities",
    )

    def __repr__(self) -> str:
        """Текстовое представление мощности рабочего центра по продукту."""
        return f"<WorkCenterCapacity(id={self.id}, wc_id={self.work_center_id}, product_id={self.product_id})>"

