"""
API routes for WorkCenter endpoints.
"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.src.models.enums import WorkCenterStatus
from backend.src.schemas.work_center import (
    WorkCenterCreate,
    WorkCenterRead,
    WorkCenterUpdate,
)
from backend.src.schemas.production_task import ProductionTaskRead
from backend.src.services.work_center_service import WorkCenterService

router = APIRouter(prefix="/api/v1/work-centers", tags=["work-centers"])


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new work center",
    description="Create a new work center with default status AVAILABLE",
)
async def create_work_center(
    payload: WorkCenterCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new work center.
    """
    service = WorkCenterService(db)

    try:
        work_center = service.create_work_center(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create work center: {str(e)}",
        )

    return {
        "success": True,
        "data": WorkCenterRead.model_validate(work_center),
    }


@router.get(
    "/{work_center_id}",
    response_model=dict,
    summary="Get work center by ID",
    description="Retrieve a work center by its ID",
)
async def get_work_center(
    work_center_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a work center by ID.
    """
    service = WorkCenterService(db)
    work_center = service.get_work_center(work_center_id)

    if not work_center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work center not found",
        )

    return {
        "success": True,
        "data": WorkCenterRead.model_validate(work_center),
    }


@router.get(
    "",
    response_model=dict,
    summary="List work centers",
    description="List work centers with optional status filter",
)
async def list_work_centers(
    status: Optional[WorkCenterStatus] = Query(None, description="Filter by work center status"),
    db: Session = Depends(get_db),
):
    """
    List work centers with optional filtering.
    """
    service = WorkCenterService(db)
    work_centers = service.list_work_centers(status=status)

    return {
        "success": True,
        "data": [WorkCenterRead.model_validate(wc) for wc in work_centers],
    }


@router.patch(
    "/{work_center_id}/status",
    response_model=dict,
    summary="Update work center status",
    description="Update work center status (AVAILABLE, BUSY, MAINTENANCE, DOWN)",
)
async def update_work_center_status(
    work_center_id: UUID,
    payload: WorkCenterUpdate,
    db: Session = Depends(get_db),
):
    """
    Update work center status.
    """
    service = WorkCenterService(db)

    # Validate status from payload
    if payload.status is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status is required",
        )

    work_center = service.update_status(work_center_id, payload.status)

    if not work_center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work center not found",
        )

    return {
        "success": True,
        "data": WorkCenterRead.model_validate(work_center),
    }


@router.get(
    "/{work_center_id}/queue",
    response_model=dict,
    summary="Get work center queue",
    description="Get queue of tasks (QUEUED and IN_PROGRESS) for a work center",
)
async def get_work_center_queue(
    work_center_id: UUID,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    db: Session = Depends(get_db),
):
    """
    Get queue of tasks for a work center.
    """
    service = WorkCenterService(db)

    # Verify work center exists
    work_center = service.get_work_center(work_center_id)
    if not work_center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work center not found",
        )

    tasks = service.get_queue(work_center_id, limit=limit, offset=offset)

    return {
        "success": True,
        "data": [ProductionTaskRead.model_validate(task) for task in tasks],
    }
