"""
DSIZ Product Work Center Routing Model.

Маршрутизация продуктов по рабочим центрам.
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.src.db.session import Base


class DSIZProductWorkCenterRouting(Base):
    """Маршрутизация продуктов по рабочим центрам."""
    
    __tablename__ = "dsiz_product_work_center_routing"
    
    id = Column(Integer, primary_key=True, index=True)
    product_sku = Column(String(50), nullable=False, index=True)
    work_center_id = Column(UUID(as_uuid=True), ForeignKey("work_centers.id"), nullable=True, index=True)
    is_allowed = Column(Boolean, nullable=False, server_default="true")
    min_quantity_for_wc = Column(Integer, nullable=True)  # напр. 5000 для авто
    priority_order = Column(Integer, nullable=True, server_default="1")  # авто > полуавто
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    
    __table_args__ = (
        UniqueConstraint('product_sku', 'work_center_id', name='uq_dsiz_routing_product_wc'),
        {"comment": "Маршрутизация продуктов по рабочим центрам с приоритетами"},
    )
