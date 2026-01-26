"""
DSIZ Changeover Matrix Model.

Матрица совместимости продуктов для расчёта времени переналадки.
"""
from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.src.db.session import Base


class DSIZChangeoverMatrix(Base):
    """Матрица совместимости продуктов для переналадки."""
    
    __tablename__ = "dsiz_changeover_matrix"
    
    id = Column(Integer, primary_key=True, index=True)
    from_compatibility_group = Column(String(100), nullable=False, index=True)
    to_compatibility_group = Column(String(100), nullable=False, index=True)
    status = Column(String(20), nullable=False)  # 'COMPATIBLE', 'INCOMPATIBLE', 'UNIVERSAL'
    setup_time_minutes = Column(Integer, nullable=False, server_default="0")
    
    __table_args__ = (
        UniqueConstraint('from_compatibility_group', 'to_compatibility_group', name='uq_dsiz_changeover_from_to'),
        {"comment": "Матрица совместимости продуктов для расчёта времени переналадки"},
    )
