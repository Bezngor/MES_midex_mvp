"""
SQLAlchemy-модель спецификации (Bill of Material).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from backend.src.db.session import Base


class BillOfMaterial(Base):
    """Модель спецификации (BOM).

    Описывает связь родительского и дочернего продукта и его количество.
    """

    __tablename__ = "bill_of_materials"

    id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    parent_product_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    child_product_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[float] = Column(Numeric(10, 4), nullable=False)
    unit: Mapped[str] = Column(String(20), nullable=False)
    sequence: Mapped[int | None] = Column(Integer, nullable=True)

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
        UniqueConstraint("parent_product_id", "child_product_id", name="uq_bom_parent_child"),
    )

    # Связи
    parent_product: Mapped["Product"] = relationship(
        "Product",
        foreign_keys=[parent_product_id],
        back_populates="bom_children",
    )
    child_product: Mapped["Product"] = relationship(
        "Product",
        foreign_keys=[child_product_id],
        back_populates="bom_parents",
    )

    def __repr__(self) -> str:
        """Текстовое представление строки спецификации."""
        return f"<BillOfMaterial(id={self.id}, parent={self.parent_product_id}, child={self.child_product_id})>"

