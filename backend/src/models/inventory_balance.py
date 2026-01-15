"""
SQLAlchemy-модель остатков на складе (InventoryBalance).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, UniqueConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from backend.src.db.session import Base
from backend.src.models.enums import ProductStatus


class InventoryBalance(Base):
    """Модель остатков по продукту и локации."""

    __tablename__ = "inventory_balances"

    id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )
    location: Mapped[str] = Column(String(100), nullable=False, index=True)
    quantity: Mapped[float] = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )
    unit: Mapped[str] = Column(String(20), nullable=False)
    # Ограничиваем значения статуса перечислением ProductStatus,
    # чтобы предотвратить появление «мусорных» значений в БД.
    product_status: Mapped[ProductStatus] = Column(
        Enum(ProductStatus, name="product_status_enum"),
        nullable=False,
        default=ProductStatus.FINISHED,
        index=True,
    )

    production_date: Mapped[datetime | None] = Column(DateTime(timezone=True), nullable=True)
    expiry_date: Mapped[datetime | None] = Column(DateTime(timezone=True), nullable=True)
    reserved_quantity: Mapped[float] = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
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

    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "location",
            "product_status",
            name="uq_inventory_product_location_status",
        ),
    )

    # Связи
    product: Mapped["Product"] = relationship("Product", back_populates="inventory_balances")

    @property
    def available_quantity(self) -> float:
        """Доступное количество (с учётом резерва)."""
        return float(self.quantity or 0) - float(self.reserved_quantity or 0)

    def __repr__(self) -> str:
        """Текстовое представление остатка."""
        return f"<InventoryBalance(id={self.id}, product_id={self.product_id}, location={self.location})>"

