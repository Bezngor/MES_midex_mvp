"""
Service for RouteOperation business logic.
"""

from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.core.models.route_operation import RouteOperation
from backend.core.models.manufacturing_route import ManufacturingRoute
from backend.core.models.work_center import WorkCenter
from backend.core.schemas.route_operation import RouteOperationCreate, RouteOperationUpdate


class OperationService:
    """Service for managing route operations."""

    def __init__(self, db: Session):
        """
        Initialize OperationService with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create_operation(self, payload: RouteOperationCreate) -> RouteOperation:
        """
        Create a new route operation.

        Args:
            payload: RouteOperationCreate schema with operation data

        Returns:
            Created RouteOperation

        Raises:
            ValueError: If route_id or work_center_id doesn't exist, or sequence is duplicate
        """
        # Validate route exists
        route = self.db.get(ManufacturingRoute, payload.route_id)
        if not route:
            raise ValueError(f"Manufacturing route not found: {payload.route_id}")

        # Validate work center exists
        work_center = self.db.get(WorkCenter, payload.work_center_id)
        if not work_center:
            raise ValueError(f"Work center not found: {payload.work_center_id}")

        # Check for duplicate sequence in the same route (optional validation)
        existing_query = select(RouteOperation).where(
            RouteOperation.route_id == payload.route_id,
            RouteOperation.operation_sequence == payload.operation_sequence,
        )
        existing_result = self.db.execute(existing_query)
        existing = existing_result.scalar_one_or_none()
        if existing:
            raise ValueError(
                f"Operation with sequence {payload.operation_sequence} already exists in this route"
            )

        operation = RouteOperation(
            route_id=payload.route_id,
            operation_sequence=payload.operation_sequence,
            operation_name=payload.operation_name,
            work_center_id=payload.work_center_id,
            estimated_duration_minutes=payload.estimated_duration_minutes,
        )
        self.db.add(operation)
        self.db.commit()
        self.db.refresh(operation)
        return operation

    def get_operation(self, operation_id: UUID) -> Optional[RouteOperation]:
        """
        Get route operation by ID.

        Args:
            operation_id: UUID of the route operation

        Returns:
            RouteOperation or None if not found
        """
        return self.db.get(RouteOperation, operation_id)

    def list_operations_by_route(self, route_id: UUID) -> list[RouteOperation]:
        """
        List all operations for a route, ordered by operation_sequence.

        Args:
            route_id: UUID of the manufacturing route

        Returns:
            List of RouteOperation objects sorted by sequence
        """
        query = (
            select(RouteOperation)
            .where(RouteOperation.route_id == route_id)
            .order_by(RouteOperation.operation_sequence)
        )
        result = self.db.execute(query)
        return list(result.scalars().all())

    def update_operation(
        self, operation_id: UUID, payload: RouteOperationUpdate
    ) -> Optional[RouteOperation]:
        """
        Update a route operation.

        Args:
            operation_id: UUID of the route operation
            payload: RouteOperationUpdate schema with fields to update

        Returns:
            Updated RouteOperation, or None if not found
        """
        operation = self.db.get(RouteOperation, operation_id)
        if not operation:
            return None

        # Validate work center if being updated
        if payload.work_center_id is not None:
            work_center = self.db.get(WorkCenter, payload.work_center_id)
            if not work_center:
                raise ValueError(f"Work center not found: {payload.work_center_id}")

        # Update fields
        if payload.operation_sequence is not None:
            operation.operation_sequence = payload.operation_sequence
        if payload.operation_name is not None:
            operation.operation_name = payload.operation_name
        if payload.work_center_id is not None:
            operation.work_center_id = payload.work_center_id
        if payload.estimated_duration_minutes is not None:
            operation.estimated_duration_minutes = payload.estimated_duration_minutes

        self.db.commit()
        self.db.refresh(operation)
        return operation

    def delete_operation(self, operation_id: UUID) -> bool:
        """
        Delete a route operation.

        Args:
            operation_id: UUID of the route operation

        Returns:
            True if deleted, False if not found
        """
        operation = self.db.get(RouteOperation, operation_id)
        if not operation:
            return False

        self.db.delete(operation)
        self.db.commit()
        return True
