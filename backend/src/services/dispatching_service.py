"""
Service for task dispatching logic.
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from backend.src.models.production_task import ProductionTask
from backend.src.models.work_center import WorkCenter
from backend.src.models.route_operation import RouteOperation
from backend.src.models.enums import TaskStatus, WorkCenterStatus


class DispatchingService:
    """Service for task dispatching and scheduling."""

    def __init__(self, db: Session):
        """
        Initialize DispatchingService with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def dispatch_tasks(self, limit: int = 50) -> list[ProductionTask]:
        """
        Preview dispatching plan: find QUEUED tasks and suggest which work centers
        can execute them (based on route operations and work center availability).

        This is a preview method that does NOT change task statuses.
        Tasks will be started manually via TaskService.start_task.

        Args:
            limit: Maximum number of tasks to consider (default: 50)

        Returns:
            List of ProductionTask objects that can be dispatched,
            sorted by created_at (FIFO), excluding tasks assigned to
            work centers with status DOWN or MAINTENANCE.
        """
        # Find all QUEUED tasks, ordered by created_at (FIFO)
        tasks_query = (
            select(ProductionTask)
            .where(ProductionTask.status == TaskStatus.QUEUED)
            .order_by(ProductionTask.created_at.asc())
            .limit(limit)
        )

        tasks_result = self.db.execute(tasks_query)
        queued_tasks = list(tasks_result.scalars().all())

        if not queued_tasks:
            return []

        # Filter tasks: exclude those assigned to unavailable work centers
        dispatchable_tasks = []
        unavailable_statuses = {WorkCenterStatus.DOWN, WorkCenterStatus.MAINTENANCE}

        for task in queued_tasks:
            # Get work center for this task
            work_center = self.db.get(WorkCenter, task.work_center_id)

            if not work_center:
                # Work center not found - skip this task
                continue

            # Check if work center is available (not DOWN or MAINTENANCE)
            if work_center.status not in unavailable_statuses:
                dispatchable_tasks.append(task)

        return dispatchable_tasks

    def get_dispatch_preview_by_work_center(
        self, limit: int = 50
    ) -> dict[str, list[ProductionTask]]:
        """
        Get dispatch preview grouped by work center.

        Args:
            limit: Maximum number of tasks to consider (default: 50)

        Returns:
            Dictionary mapping work center ID to list of dispatchable tasks
        """
        dispatchable_tasks = self.dispatch_tasks(limit=limit)

        # Group by work center
        by_work_center: dict[str, list[ProductionTask]] = {}
        for task in dispatchable_tasks:
            wc_id_str = str(task.work_center_id)
            if wc_id_str not in by_work_center:
                by_work_center[wc_id_str] = []
            by_work_center[wc_id_str].append(task)

        return by_work_center
