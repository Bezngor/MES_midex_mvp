"""
SQLAlchemy model for ManufacturingRoute.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.db.session import Base


class ManufacturingRoute(Base):
    """Manufacturing route model."""

    __tablename__ = "manufacturing_routes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    product_id = Column(String, nullable=False)
    route_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    route_operations = relationship(
        "RouteOperation",
        back_populates="manufacturing_route",
        order_by="RouteOperation.operation_sequence",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<ManufacturingRoute(id={self.id}, route_name={self.route_name}, product_id={self.product_id})>"
