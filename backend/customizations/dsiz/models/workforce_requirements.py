"""
DSIZ Workforce Requirements Model.

Нормы укомплектованности персоналом для рабочих центров.
"""
from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.src.db.session import Base


class DSIZWorkforceRequirements(Base):
    """Нормы укомплектованности персоналом для рабочих центров."""
    
    __tablename__ = "dsiz_workforce_requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    work_center_id = Column(UUID(as_uuid=True), ForeignKey("work_centers.id"), nullable=True, index=True)
    role_name = Column(String(50), nullable=False, index=True)  # 'OPERATOR', 'PACKER'
    required_count = Column(Integer, nullable=False)
    is_mandatory = Column(Boolean, nullable=False, server_default="true")
    min_count_for_degraded_mode = Column(Integer, nullable=True)  # напр. 3 из 4
    degradation_factor = Column(Numeric(3, 2), nullable=True)  # 0.5 при 3/4 операторах
    
    __table_args__ = (
        UniqueConstraint('work_center_id', 'role_name', name='uq_dsiz_workforce_wc_role'),
        {"comment": "Нормы укомплектованности персоналом с учётом деградации производительности"},
    )
