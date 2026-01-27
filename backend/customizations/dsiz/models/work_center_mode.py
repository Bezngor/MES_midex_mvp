"""
DSIZ Work Center Mode Model.

Режимы работы реактора (CREAM_MODE, PASTE_MODE и т.д.).
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.src.db.session import Base


class DSIZWorkCenterMode(Base):
    """Режимы работы рабочего центра (реактора)."""
    
    __tablename__ = "dsiz_work_center_modes"
    
    id = Column(Integer, primary_key=True, index=True)
    work_center_id = Column(UUID(as_uuid=True), ForeignKey("work_centers.id"), nullable=False, index=True)
    mode_name = Column(String(50), nullable=False)  # 'CREAM_MODE', 'PASTE_MODE'
    min_load_kg = Column(Numeric(10, 2), nullable=False)
    max_load_kg = Column(Numeric(10, 2), nullable=False)
    cycle_duration_hours = Column(Integer, nullable=False)  # 4 or 5
    max_cycles_per_shift = Column(Integer, nullable=False, server_default="2")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    
    __table_args__ = (
        UniqueConstraint('work_center_id', 'mode_name', name='uq_dsiz_wc_modes_wc_mode'),
        {"comment": "Режимы работы реактора (минимальная/максимальная загрузка, длительность цикла)"},
    )
