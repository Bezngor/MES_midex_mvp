"""
Service for WorkCenter business logic.
"""

from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_

from backend.core.models.work_center import WorkCenter
from backend.core.models.production_task import ProductionTask
from backend.core.models.enums import WorkCenterStatus, TaskStatus
from backend.core.schemas.work_center import WorkCenterCreate


class WorkCenterService:
    """Service for managing work centers."""

    def __init__(self, db: Session):
        """
        Initialize WorkCenterService with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create_work_center(self, payload: WorkCenterCreate) -> WorkCenter:
        """
        Create a new work center.

        Args:
            payload: WorkCenterCreate schema with work center data

        Returns:
            Created WorkCenter
        """
        work_center = WorkCenter(
            name=payload.name,
            resource_type=payload.resource_type,
            status=payload.status,
            capacity_units_per_hour=payload.capacity_units_per_hour,
        )
        self.db.add(work_center)
        self.db.commit()
        self.db.refresh(work_center)
        return work_center

    def get_work_center(self, work_center_id: UUID) -> Optional[WorkCenter]:
        """
        Get work center by ID.

        Args:
            work_center_id: UUID of the work center

        Returns:
            WorkCenter or None if not found
        """
        return self.db.get(WorkCenter, work_center_id)

    def list_work_centers(
        self, status: Optional[WorkCenterStatus] = None
    ) -> list[WorkCenter]:
        """
        List work centers with optional status filter.

        Args:
            status: Optional WorkCenterStatus to filter by

        Returns:
            List of WorkCenter objects
        """
        query = select(WorkCenter)

        if status:
            query = query.where(WorkCenter.status == status)

        query = query.order_by(WorkCenter.name)

        result = self.db.execute(query)
        return list(result.scalars().all())

    def update_status(
        self, work_center_id: UUID, status: WorkCenterStatus
    ) -> Optional[WorkCenter]:
        """
        Update work center status.

        Args:
            work_center_id: UUID of the work center
            status: New WorkCenterStatus

        Returns:
            Updated WorkCenter, or None if not found
        """
        work_center = self.db.get(WorkCenter, work_center_id)
        if not work_center:
            return None

        work_center.status = status
        self.db.commit()
        self.db.refresh(work_center)
        return work_center

    def get_queue(
        self, work_center_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[ProductionTask]:
        """
        Get queue of tasks for a work center (QUEUED and IN_PROGRESS tasks).

        Args:
            work_center_id: UUID of the work center
            limit: Maximum number of tasks to return (default: 50)
            offset: Number of tasks to skip (default: 0)

        Returns:
            List of ProductionTask objects (QUEUED and IN_PROGRESS)
        """
        query = (
            select(ProductionTask)
            .where(
                and_(
                    ProductionTask.work_center_id == work_center_id,
                    or_(
                        ProductionTask.status == TaskStatus.QUEUED,
                        ProductionTask.status == TaskStatus.IN_PROGRESS,
                    ),
                )
            )
            .order_by(ProductionTask.created_at.asc())
            .limit(limit)
            .offset(offset)
        )

        result = self.db.execute(query)
        return list(result.scalars().all())
