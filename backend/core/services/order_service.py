"""
Service for ManufacturingOrder business logic.
"""

from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.manufacturing_route import ManufacturingRoute
from backend.core.models.route_operation import RouteOperation
from backend.core.models.production_task import ProductionTask
from backend.core.models.enums import OrderStatus, TaskStatus
from backend.core.schemas.manufacturing_order import ManufacturingOrderCreate


class OrderService:
    """Service for managing manufacturing orders."""

    def __init__(self, db: Session):
        """
        Initialize OrderService with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create_order_with_tasks(self, payload: ManufacturingOrderCreate) -> ManufacturingOrder:
        """
        Create a manufacturing order and generate production tasks from route.

        Args:
            payload: ManufacturingOrderCreate schema with order data

        Returns:
            Created ManufacturingOrder with associated ProductionTasks

        Raises:
            ValueError: If quantity is invalid or manufacturing route not found
        """
        # Validate quantity
        if payload.quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        # Find manufacturing route by product_id
        route_query = select(ManufacturingRoute).where(
            ManufacturingRoute.product_id == payload.product_id
        )
        route_result = self.db.execute(route_query)
        route = route_result.scalar_one_or_none()

        if not route:
            raise ValueError(
                f"Manufacturing route not found for product_id: {payload.product_id}"
            )

        # Load route operations ordered by sequence
        route_operations_query = (
            select(RouteOperation)
            .where(RouteOperation.route_id == route.id)
            .order_by(RouteOperation.operation_sequence)
        )
        route_operations_result = self.db.execute(route_operations_query)
        route_operations = route_operations_result.scalars().all()

        if not route_operations:
            raise ValueError(
                f"Manufacturing route '{route.route_name}' has no operations defined"
            )

        # Create manufacturing order
        order = ManufacturingOrder(
            order_number=payload.order_number,
            product_id=payload.product_id,
            quantity=payload.quantity,
            status=OrderStatus.PLANNED,
            due_date=payload.due_date,
        )
        self.db.add(order)
        self.db.flush()  # Flush to get order.id

        # Create production tasks for each route operation
        tasks = []
        for route_operation in route_operations:
            task = ProductionTask(
                order_id=order.id,
                operation_id=route_operation.id,
                work_center_id=route_operation.work_center_id,
                status=TaskStatus.QUEUED,
            )
            tasks.append(task)
            self.db.add(task)

        # Commit transaction
        self.db.commit()
        
        # Reload order with tasks using eager loading
        order_query = (
            select(ManufacturingOrder)
            .options(joinedload(ManufacturingOrder.production_tasks))
            .where(ManufacturingOrder.id == order.id)
        )
        result = self.db.execute(order_query)
        order_with_tasks = result.unique().scalar_one()
        return order_with_tasks

    def get_order_with_tasks(self, order_id: UUID) -> Optional[ManufacturingOrder]:
        """
        Get manufacturing order by ID with associated production tasks.

        Args:
            order_id: UUID of the manufacturing order

        Returns:
            ManufacturingOrder with loaded production_tasks, or None if not found
        """
        query = (
            select(ManufacturingOrder)
            .options(joinedload(ManufacturingOrder.production_tasks))
            .where(ManufacturingOrder.id == order_id)
        )
        result = self.db.execute(query)
        return result.unique().scalar_one_or_none()

    def list_orders(
        self,
        status: Optional[OrderStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ManufacturingOrder]:
        """
        List manufacturing orders with optional status filter and pagination.

        Args:
            status: Optional OrderStatus to filter by
            limit: Maximum number of orders to return (default: 50)
            offset: Number of orders to skip (default: 0)

        Returns:
            List of ManufacturingOrder objects
        """
        query = select(ManufacturingOrder)

        if status:
            query = query.where(ManufacturingOrder.status == status)

        query = query.order_by(ManufacturingOrder.created_at.desc()).limit(limit).offset(offset)

        result = self.db.execute(query)
        return list(result.scalars().all())

    def update_order_status(self, order_id: UUID, status: OrderStatus) -> Optional[ManufacturingOrder]:
        """
        Update manufacturing order status.

        Args:
            order_id: UUID of the manufacturing order
            status: New OrderStatus

        Returns:
            Updated ManufacturingOrder, or None if not found
        """
        order = self.db.get(ManufacturingOrder, order_id)
        if not order:
            return None

        order.status = status
        self.db.commit()
        self.db.refresh(order)
        return order
