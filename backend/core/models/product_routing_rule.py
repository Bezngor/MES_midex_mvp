"""
SQLAlchemy model for ProductRoutingRule.

Правила выбора РЦ для ГП: продукт, допустимые РЦ, приоритет, min/max количество.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.db.session import Base


class ProductRoutingRule(Base):
    """Правило выбора рабочего центра для продукта (ГП)."""

    __tablename__ = "product_routing_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    product_code = Column(String, nullable=False)
    work_center_id = Column(UUID(as_uuid=True), ForeignKey("work_centers.id", ondelete="CASCADE"), nullable=False)
    priority_order = Column(Integer, nullable=False)
    min_quantity = Column(Integer, nullable=True)
    max_quantity = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    work_center = relationship("WorkCenter", backref="product_routing_rules")

    def __repr__(self):
        return f"<ProductRoutingRule(product_code={self.product_code!r}, work_center_id={self.work_center_id}, priority={self.priority_order})>"
