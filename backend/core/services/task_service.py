"""
Service for ProductionTask business logic and WIP tracking.
"""

from uuid import UUID
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select, and_

from backend.core.models.production_task import ProductionTask
from backend.core.models.genealogy_record import GenealogyRecord
from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.enums import TaskStatus, OrderStatus


class TaskService:
    """Service for managing production tasks and WIP tracking."""

    def __init__(self, db: Session):
        """
        Initialize TaskService with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        work_center_id: Optional[UUID] = None,
        order_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProductionTask]:
        """
        List production tasks with optional filters and pagination.

        Args:
            status: Optional TaskStatus to filter by
            work_center_id: Optional UUID to filter by work center
            order_id: Optional UUID to filter by manufacturing order
            limit: Maximum number of tasks to return (default: 50)
            offset: Number of tasks to skip (default: 0)

        Returns:
            List of ProductionTask objects
        """
        query = select(ProductionTask)

        # Apply filters
        conditions = []
        if status:
            conditions.append(ProductionTask.status == status)
        if work_center_id:
            conditions.append(ProductionTask.work_center_id == work_center_id)
        if order_id:
            conditions.append(ProductionTask.order_id == order_id)

        if conditions:
            query = query.where(and_(*conditions))

        # Order by creation date (newest first) and apply pagination
        query = query.order_by(ProductionTask.created_at.desc()).limit(limit).offset(offset)

        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_task_with_relations(self, task_id: UUID) -> Optional[ProductionTask]:
        """
        Get production task by ID with all related entities loaded.

        Args:
            task_id: UUID of the production task

        Returns:
            ProductionTask with loaded relations, or None if not found
        """
        query = (
            select(ProductionTask)
            .options(
                joinedload(ProductionTask.manufacturing_order),
                joinedload(ProductionTask.route_operation),
                joinedload(ProductionTask.work_center),
                selectinload(ProductionTask.genealogy_records),
                selectinload(ProductionTask.quality_inspections),
            )
            .where(ProductionTask.id == task_id)
        )
        result = self.db.execute(query)
        return result.unique().scalar_one_or_none()

    def start_task(self, task_id: UUID, operator_id: Optional[str] = None) -> ProductionTask:
        """
        Start a production task (change status from QUEUED to IN_PROGRESS).

        Args:
            task_id: UUID of the production task
            operator_id: Optional operator ID who is starting the task

        Returns:
            Updated ProductionTask

        Raises:
            ValueError: If task not found or status is not QUEUED
        """
        task = self.db.get(ProductionTask, task_id)
        if not task:
            raise ValueError(f"Production task not found: {task_id}")

        if task.status != TaskStatus.QUEUED:
            raise ValueError(
                f"Cannot start task with status {task.status.value}. Task must be QUEUED."
            )

        # Update task status and timestamps
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now(timezone.utc)
        if operator_id:
            task.assigned_to = operator_id

        # Create genealogy record
        genealogy_record = GenealogyRecord(
            task_id=task.id,
            operator_id=operator_id or "system",
            event_type="STARTED",
            timestamp=datetime.now(timezone.utc),
            notes=None,
        )
        self.db.add(genealogy_record)

        self.db.commit()
        self.db.refresh(task)
        return task

    def complete_task(self, task_id: UUID, notes: Optional[str] = None) -> ProductionTask:
        """
        Complete a production task (change status from IN_PROGRESS to COMPLETED).

        Args:
            task_id: UUID of the production task
            notes: Optional completion notes

        Returns:
            Updated ProductionTask

        Raises:
            ValueError: If task not found or status is not IN_PROGRESS
        """
        task = self.db.get(ProductionTask, task_id)
        if not task:
            raise ValueError(f"Production task not found: {task_id}")

        if task.status != TaskStatus.IN_PROGRESS:
            raise ValueError(
                f"Cannot complete task with status {task.status.value}. Task must be IN_PROGRESS."
            )

        # Update task status and completion timestamp
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now(timezone.utc)

        # Create genealogy record
        genealogy_record = GenealogyRecord(
            task_id=task.id,
            operator_id=task.assigned_to or "system",
            event_type="COMPLETED",
            timestamp=datetime.now(timezone.utc),
            notes=notes,
        )
        self.db.add(genealogy_record)

        # Check if all tasks of the order are completed
        self._check_and_update_order_status(task.order_id)

        self.db.commit()
        self.db.refresh(task)
        return task

    def fail_task(self, task_id: UUID, reason: str) -> ProductionTask:
        """
        Mark a production task as failed.

        Args:
            task_id: UUID of the production task
            reason: Reason for failure

        Returns:
            Updated ProductionTask

        Raises:
            ValueError: If task not found
        """
        task = self.db.get(ProductionTask, task_id)
        if not task:
            raise ValueError(f"Production task not found: {task_id}")

        # Update task status
        task.status = TaskStatus.FAILED

        # Create genealogy record
        genealogy_record = GenealogyRecord(
            task_id=task.id,
            operator_id=task.assigned_to or "system",
            event_type="FAILED",
            timestamp=datetime.now(timezone.utc),
            notes=reason,
        )
        self.db.add(genealogy_record)

        self.db.commit()
        self.db.refresh(task)
        return task

    def _check_and_update_order_status(self, order_id: UUID) -> None:
        """
        Check if all tasks of an order are completed and update order status if so.

        Args:
            order_id: UUID of the manufacturing order
        """
        # Get all tasks for this order
        tasks_query = select(ProductionTask).where(ProductionTask.order_id == order_id)
        tasks_result = self.db.execute(tasks_query)
        tasks = list(tasks_result.scalars().all())

        if not tasks:
            return

        # Check if all tasks are completed
        all_completed = all(task.status == TaskStatus.COMPLETED for task in tasks)

        if all_completed:
            # Update order status to COMPLETED
            order = self.db.get(ManufacturingOrder, order_id)
            if order and order.status != OrderStatus.COMPLETED:
                order.status = OrderStatus.COMPLETED
                self.db.flush()
