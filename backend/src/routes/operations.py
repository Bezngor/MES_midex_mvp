"""
API routes for RouteOperation endpoints.
"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.src.schemas.route_operation import (
    RouteOperationCreate,
    RouteOperationRead,
    RouteOperationUpdate,
)
from backend.src.services.operation_service import OperationService

router = APIRouter(prefix="/api/v1/route-operations", tags=["route-operations"])


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new route operation",
    description="Create a new route operation in a manufacturing route",
)
async def create_route_operation(
    payload: RouteOperationCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new route operation.
    """
    service = OperationService(db)

    try:
        operation = service.create_operation(payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create route operation: {str(e)}",
        )

    return {
        "success": True,
        "data": RouteOperationRead.model_validate(operation),
    }


@router.get(
    "/{operation_id}",
    response_model=dict,
    summary="Get route operation by ID",
    description="Retrieve a route operation by its ID",
)
async def get_route_operation(
    operation_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a route operation by ID.
    """
    service = OperationService(db)
    operation = service.get_operation(operation_id)

    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route operation not found",
        )

    return {
        "success": True,
        "data": RouteOperationRead.model_validate(operation),
    }


@router.get(
    "",
    response_model=dict,
    summary="List route operations",
    description="List route operations, optionally filtered by route_id",
)
async def list_route_operations(
    route_id: Optional[UUID] = Query(None, description="Filter by route ID"),
    db: Session = Depends(get_db),
):
    """
    List route operations, optionally filtered by route_id.
    """
    service = OperationService(db)

    if route_id:
        operations = service.list_operations_by_route(route_id)
    else:
        # If no route_id, return empty list or all operations
        # For now, require route_id for listing
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="route_id query parameter is required",
        )

    return {
        "success": True,
        "data": [RouteOperationRead.model_validate(op) for op in operations],
    }


@router.patch(
    "/{operation_id}",
    response_model=dict,
    summary="Update route operation",
    description="Update a route operation (sequence, name, work center, duration)",
)
async def update_route_operation(
    operation_id: UUID,
    payload: RouteOperationUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a route operation.
    """
    service = OperationService(db)

    try:
        operation = service.update_operation(operation_id, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update route operation: {str(e)}",
        )

    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route operation not found",
        )

    return {
        "success": True,
        "data": RouteOperationRead.model_validate(operation),
    }


@router.delete(
    "/{operation_id}",
    response_model=dict,
    summary="Delete route operation",
    description="Delete a route operation",
)
async def delete_route_operation(
    operation_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Delete a route operation.
    """
    service = OperationService(db)
    deleted = service.delete_operation(operation_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route operation not found",
        )

    return {
        "success": True,
        "data": {"message": "Route operation deleted successfully"},
    }
