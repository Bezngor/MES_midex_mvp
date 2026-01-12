"""
API routes for task dispatching endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.src.schemas.production_task import ProductionTaskRead
from backend.src.services.dispatching_service import DispatchingService

router = APIRouter(prefix="/api/v1/dispatch", tags=["dispatch"])


@router.post(
    "/preview",
    response_model=dict,
    summary="Preview dispatch plan",
    description="Preview tasks that can be dispatched without changing their statuses. "
                "Returns QUEUED tasks that are assigned to available work centers "
                "(excluding DOWN/MAINTENANCE status).",
)
async def preview_dispatch(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tasks to consider"),
    db: Session = Depends(get_db),
):
    """
    Preview dispatch plan.

    This endpoint returns a list of tasks that can be dispatched based on:
    - Task status is QUEUED
    - Work center is available (not DOWN or MAINTENANCE)
    - FIFO ordering (oldest tasks first)

    The tasks are NOT automatically started. Use the start_task endpoint
    to actually begin execution.
    """
    service = DispatchingService(db)
    dispatchable_tasks = service.dispatch_tasks(limit=limit)

    return {
        "success": True,
        "data": [ProductionTaskRead.model_validate(task) for task in dispatchable_tasks],
    }
