"""
Service for ManufacturingRoute business logic.
"""

from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from backend.src.models.manufacturing_route import ManufacturingRoute
from backend.src.schemas.manufacturing_route import ManufacturingRouteCreate


class RouteService:
    """Service for managing manufacturing routes."""

    def __init__(self, db: Session):
        """
        Initialize RouteService with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create_route(self, payload: ManufacturingRouteCreate) -> ManufacturingRoute:
        """
        Create a new manufacturing route.

        Args:
            payload: ManufacturingRouteCreate schema with route data

        Returns:
            Created ManufacturingRoute
        """
        route = ManufacturingRoute(
            product_id=payload.product_id,
            route_name=payload.route_name,
            description=payload.description,
        )
        self.db.add(route)
        self.db.commit()
        self.db.refresh(route)
        return route

    def get_route(self, route_id: UUID) -> Optional[ManufacturingRoute]:
        """
        Get manufacturing route by ID with loaded route operations.

        Args:
            route_id: UUID of the manufacturing route

        Returns:
            ManufacturingRoute with loaded route_operations, or None if not found
        """
        query = (
            select(ManufacturingRoute)
            .options(joinedload(ManufacturingRoute.route_operations))
            .where(ManufacturingRoute.id == route_id)
        )
        result = self.db.execute(query)
        return result.unique().scalar_one_or_none()

    def get_route_by_product(self, product_id: str) -> Optional[ManufacturingRoute]:
        """
        Find manufacturing route by product_id with loaded route operations.

        Args:
            product_id: Product ID to search for

        Returns:
            ManufacturingRoute with loaded route_operations, or None if not found
        """
        query = (
            select(ManufacturingRoute)
            .options(joinedload(ManufacturingRoute.route_operations))
            .where(ManufacturingRoute.product_id == product_id)
        )
        result = self.db.execute(query)
        return result.unique().scalar_one_or_none()

    def list_routes(self) -> list[ManufacturingRoute]:
        """
        List all manufacturing routes.

        Returns:
            List of ManufacturingRoute objects
        """
        query = select(ManufacturingRoute).order_by(ManufacturingRoute.route_name)
        result = self.db.execute(query)
        return list(result.scalars().all())

    def delete_route(self, route_id: UUID) -> bool:
        """
        Delete a manufacturing route.

        Args:
            route_id: UUID of the manufacturing route

        Returns:
            True if deleted, False if not found
        """
        route = self.db.get(ManufacturingRoute, route_id)
        if not route:
            return False

        self.db.delete(route)
        self.db.commit()
        return True
