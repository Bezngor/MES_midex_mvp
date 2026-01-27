"""
DSIZ Base Rates Model.

Базовые скорости операций для продуктов на рабочих центрах.
"""
from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.src.db.session import Base


class DSIZBaseRates(Base):
    """Базовые скорости операций для продуктов."""
    
    __tablename__ = "dsiz_base_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    product_sku = Column(String(50), nullable=False, index=True)
    work_center_id = Column(UUID(as_uuid=True), ForeignKey("work_centers.id"), nullable=True, index=True)
    base_rate_units_per_hour = Column(Numeric(10, 2), nullable=False)
    is_human_dependent = Column(Boolean, nullable=False, server_default="false")
    
    __table_args__ = (
        {"comment": "Базовые скорости операций для продуктов на рабочих центрах"},
    )
