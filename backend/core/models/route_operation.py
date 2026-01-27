"""
SQLAlchemy model for RouteOperation.
"""

import uuid
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.db.session import Base


class RouteOperation(Base):
    """Route operation model."""

    __tablename__ = "route_operations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    route_id = Column(UUID(as_uuid=True), ForeignKey("manufacturing_routes.id", ondelete="CASCADE"), nullable=False)
    operation_sequence = Column(Integer, nullable=False)
    operation_name = Column(String, nullable=False)
    work_center_id = Column(UUID(as_uuid=True), ForeignKey("work_centers.id"), nullable=False)
    estimated_duration_minutes = Column(Integer, nullable=False)

    # Relationships
    manufacturing_route = relationship("ManufacturingRoute", back_populates="route_operations")
    work_center = relationship("WorkCenter", back_populates="route_operations")
    production_tasks = relationship("ProductionTask", back_populates="route_operation")

    def __repr__(self):
        return f"<RouteOperation(id={self.id}, operation_name={self.operation_name}, sequence={self.operation_sequence})>"
