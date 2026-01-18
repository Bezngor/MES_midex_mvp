"""
SQLAlchemy-модель для продуктов (сырьё, полуфабрикаты, упаковка, ГП).
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from backend.src.db.session import Base
from backend.core.models.enums import ProductType


class Product(Base):
    """Модель продукта.

    Описывает сырьё, bulk-продукты, упаковку и готовую продукцию.
    """

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    product_code: Mapped[str] = Column(String(100), unique=True, nullable=False, index=True)
    product_name: Mapped[str] = Column(String(255), nullable=False)
    product_type: Mapped[str] = Column(String(50), nullable=False, index=True)
    unit_of_measure: Mapped[str] = Column(String(20), nullable=False)

    # Для BULK-продуктов
    min_batch_size_kg: Mapped[float | None] = Column(Numeric(10, 2), nullable=True)
    batch_size_step_kg: Mapped[float | None] = Column(Numeric(10, 2), nullable=True)
    shelf_life_days: Mapped[int | None] = Column(
        # Используем целое количество дней хранения.
        # В БД храним как Integer (см. миграцию).
        Numeric(10, 0),
        nullable=True,
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
    bom_parents: Mapped[List["BillOfMaterial"]] = relationship(
        "BillOfMaterial",
        foreign_keys="BillOfMaterial.child_product_id",
        back_populates="child_product",
    )
    bom_children: Mapped[List["BillOfMaterial"]] = relationship(
        "BillOfMaterial",
        foreign_keys="BillOfMaterial.parent_product_id",
        back_populates="parent_product",
    )
    inventory_balances: Mapped[List["InventoryBalance"]] = relationship(
        "InventoryBalance",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    work_center_capacities: Mapped[List["WorkCenterCapacity"]] = relationship(
        "WorkCenterCapacity",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    batches: Mapped[List["Batch"]] = relationship(
        "Batch",
        back_populates="product",
    )

    def __repr__(self) -> str:
        """Текстовое представление продукта."""
        return f"<Product(id={self.id}, code={self.product_code}, type={self.product_type})>"

