"""
API routes for ProductionTask endpoints.
"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.src.models.enums import TaskStatus
from backend.src.schemas.production_task import (
    ProductionTaskRead,
    TaskStartPayload,
    TaskCompletePayload,
    TaskFailPayload,
)
from backend.src.services.task_service import TaskService

router = APIRouter(prefix="/api/v1/production-tasks", tags=["production-tasks"])


@router.get(
    "",
    response_model=dict,
    summary="List production tasks",
    description="List production tasks with optional filters (status, work_center_id, order_id) and pagination",
)
async def list_production_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    work_center_id: Optional[UUID] = Query(None, description="Filter by work center ID"),
    order_id: Optional[UUID] = Query(None, description="Filter by manufacturing order ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    db: Session = Depends(get_db),
):
    """
    List production tasks with optional filtering and pagination.
    """
    service = TaskService(db)
    tasks = service.list_tasks(
        status=status,
        work_center_id=work_center_id,
        order_id=order_id,
        limit=limit,
        offset=offset,
    )

    return {
        "success": True,
        "data": [ProductionTaskRead.model_validate(task) for task in tasks],
    }


@router.get(
    "/{task_id}",
    response_model=dict,
    summary="Get production task by ID",
    description="Retrieve a production task with all related entities (order, route operation, work center, genealogy, quality)",
)
async def get_production_task(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a production task by ID with all related entities.
    """
    service = TaskService(db)
    task = service.get_task_with_relations(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production task not found",
        )

    return {
        "success": True,
        "data": ProductionTaskRead.model_validate(task),
    }


@router.patch(
    "/{task_id}/start",
    response_model=dict,
    summary="Start a production task",
    description="Start a production task (change status from QUEUED to IN_PROGRESS)",
)
async def start_production_task(
    task_id: UUID,
    payload: TaskStartPayload | None = None,
    db: Session = Depends(get_db),
):
    """
    Start a production task.

    The task must be in QUEUED status. This will:
    - Change status to IN_PROGRESS
    - Set started_at timestamp
    - Optionally assign operator_id
    - Create a genealogy record with event_type="STARTED"
    """
    service = TaskService(db)

    try:
        operator_id = payload.operator_id if payload else None
        task = service.start_task(task_id, operator_id=operator_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start production task: {str(e)}",
        )

    return {
        "success": True,
        "data": ProductionTaskRead.model_validate(task),
    }


@router.patch(
    "/{task_id}/complete",
    response_model=dict,
    summary="Complete a production task",
    description="Complete a production task (change status from IN_PROGRESS to COMPLETED)",
)
async def complete_production_task(
    task_id: UUID,
    payload: TaskCompletePayload | None = None,
    db: Session = Depends(get_db),
):
    """
    Complete a production task.

    The task must be in IN_PROGRESS status. This will:
    - Change status to COMPLETED
    - Set completed_at timestamp
    - Create a genealogy record with event_type="COMPLETED"
    - If all tasks of the order are completed, update order status to COMPLETED
    """
    service = TaskService(db)

    try:
        notes = payload.notes if payload else None
        task = service.complete_task(task_id, notes=notes)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete production task: {str(e)}",
        )

    return {
        "success": True,
        "data": ProductionTaskRead.model_validate(task),
    }


@router.patch(
    "/{task_id}/fail",
    response_model=dict,
    summary="Mark a production task as failed",
    description="Mark a production task as failed (set status to FAILED)",
)
async def fail_production_task(
    task_id: UUID,
    payload: TaskFailPayload,
    db: Session = Depends(get_db),
):
    """
    Mark a production task as failed.

    This will:
    - Change status to FAILED
    - Create a genealogy record with event_type="FAILED" and the provided reason
    """
    service = TaskService(db)

    try:
        task = service.fail_task(task_id, reason=payload.reason)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark production task as failed: {str(e)}",
        )

    return {
        "success": True,
        "data": ProductionTaskRead.model_validate(task),
    }
