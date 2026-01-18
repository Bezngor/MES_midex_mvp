"""
API routes for ManufacturingOrder endpoints.
"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.core.models.enums import OrderStatus
from backend.core.schemas.manufacturing_order import (
    ManufacturingOrderCreate,
    ManufacturingOrderRead,
    ManufacturingOrderWithTasksRead,
)
from backend.core.services.order_service import OrderService

router = APIRouter(prefix="/api/v1/manufacturing-orders", tags=["manufacturing-orders"])


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new manufacturing order",
    description="Create a manufacturing order and automatically generate production tasks based on the product's manufacturing route",
)
async def create_manufacturing_order(
    payload: ManufacturingOrderCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new manufacturing order.

    The order will be created with status PLANNED and production tasks will be
    automatically generated based on the manufacturing route for the specified product_id.
    """
    service = OrderService(db)

    try:
        order = service.create_order_with_tasks(payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create manufacturing order: {str(e)}",
        )

    return {
        "success": True,
        "data": ManufacturingOrderRead.model_validate(order),
    }


@router.get(
    "/{order_id}",
    response_model=dict,
    summary="Get manufacturing order by ID with tasks",
    description="Retrieve a manufacturing order with all associated production tasks",
)
async def get_manufacturing_order(
    order_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get a manufacturing order by ID with associated production tasks.
    """
    service = OrderService(db)
    order = service.get_order_with_tasks(order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manufacturing order not found",
        )

    return {
        "success": True,
        "data": ManufacturingOrderWithTasksRead.model_validate(order),
    }


@router.get(
    "",
    response_model=dict,
    summary="List manufacturing orders",
    description="List manufacturing orders with optional status filter and pagination",
)
async def list_manufacturing_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip"),
    db: Session = Depends(get_db),
):
    """
    List manufacturing orders with optional filtering and pagination.
    """
    service = OrderService(db)
    orders = service.list_orders(status=status, limit=limit, offset=offset)

    return {
        "success": True,
        "data": [ManufacturingOrderRead.model_validate(order) for order in orders],
    }
