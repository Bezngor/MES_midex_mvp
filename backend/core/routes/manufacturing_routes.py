"""
API routes for ManufacturingRoute endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.core.schemas.manufacturing_route import (
    ManufacturingRouteCreate,
    ManufacturingRouteRead,
    ManufacturingRouteWithOperationsRead,
)
from backend.core.services.route_service import RouteService

router = APIRouter(prefix="/api/v1/manufacturing-routes", tags=["manufacturing-routes"])


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new manufacturing route",
    description="Create a new manufacturing route for a product",
)
async def create_manufacturing_route(
    payload: ManufacturingRouteCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new manufacturing route.
    """
    service = RouteService(db)

    try:
        route = service.create_route(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create manufacturing route: {str(e)}",
        )

    return {
        "success": True,
        "data": ManufacturingRouteRead.model_validate(route),
    }


@router.get(
    "/{route_id}",
    response_model=dict,
    summary="Get manufacturing route by ID",
    description="Retrieve a manufacturing route with all associated route operations",
)
async def get_manufacturing_route(
    route_id: str,
    db: Session = Depends(get_db),
):
    """
    Get a manufacturing route by ID with route operations.
    """
    from uuid import UUID

    try:
        route_uuid = UUID(route_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid route ID format",
        )

    service = RouteService(db)
    route = service.get_route(route_uuid)

    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manufacturing route not found",
        )

    return {
        "success": True,
        "data": ManufacturingRouteWithOperationsRead.model_validate(route),
    }


@router.get(
    "",
    response_model=dict,
    summary="List manufacturing routes",
    description="List all manufacturing routes",
)
async def list_manufacturing_routes(
    db: Session = Depends(get_db),
):
    """
    List all manufacturing routes.
    """
    service = RouteService(db)
    routes = service.list_routes()

    return {
        "success": True,
        "data": [ManufacturingRouteRead.model_validate(route) for route in routes],
    }


@router.get(
    "/by-product/{product_id}",
    response_model=dict,
    summary="Get manufacturing route by product ID",
    description="Find manufacturing route for a specific product",
)
async def get_manufacturing_route_by_product(
    product_id: str,
    db: Session = Depends(get_db),
):
    """
    Get manufacturing route by product ID with route operations.
    """
    service = RouteService(db)
    route = service.get_route_by_product(product_id)

    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manufacturing route not found for product_id: {product_id}",
        )

    return {
        "success": True,
        "data": ManufacturingRouteWithOperationsRead.model_validate(route),
    }


@router.delete(
    "/{route_id}",
    response_model=dict,
    summary="Delete manufacturing route",
    description="Delete a manufacturing route (cascade deletes all route operations)",
)
async def delete_manufacturing_route(
    route_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete a manufacturing route.
    """
    from uuid import UUID

    try:
        route_uuid = UUID(route_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid route ID format",
        )

    service = RouteService(db)
    deleted = service.delete_route(route_uuid)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manufacturing route not found",
        )

    return {
        "success": True,
        "data": {"message": "Manufacturing route deleted successfully"},
    }
