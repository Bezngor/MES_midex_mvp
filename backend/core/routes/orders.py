"""
API routes for ManufacturingOrder endpoints.
"""

from uuid import UUID
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.core.models.enums import OrderStatus
from backend.core.models.product import Product
from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.schemas.manufacturing_order import (
    ManufacturingOrderCreate,
    ManufacturingOrderRead,
    ManufacturingOrderWithTasksRead,
)
from backend.core.services.order_service import OrderService
from backend.core.services.order_comparison_service import OrderComparisonService
from backend.core.schemas.order_changes import (
    OrderChangesListResponse,
    OrderChangeDetailResponse,
    OrderChangeInfo,
)
from backend.core.models.enums import OrderType

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
    В ответ добавляются product_name и product_code для отображения в UI.
    """
    service = OrderService(db)
    orders = service.list_orders(status=status, limit=limit, offset=offset)

    product_ids = []
    for o in orders:
        try:
            product_ids.append(UUID(str(o.product_id)))
        except (ValueError, TypeError):
            pass
    products = db.query(Product).filter(Product.id.in_(product_ids)).all() if product_ids else []
    product_info = {str(p.id): {"name": p.product_name, "code": p.product_code} for p in products}

    data = []
    for order in orders:
        row = ManufacturingOrderRead.model_validate(order).model_dump()
        info = product_info.get(str(order.product_id))
        row["product_name"] = info["name"] if info else None
        row["product_code"] = info["code"] if info else None
        data.append(row)

    return {
        "success": True,
        "data": data,
    }


@router.get(
    "/changes",
    response_model=OrderChangesListResponse,
    summary="Get list of new and changed orders",
    description="Выявить новые и/или измененные ЗП (бизнес-процесс: Блок обновления данных)",
)
async def get_order_changes(
    order_type: Optional[str] = Query(
        default=OrderType.CUSTOMER.value,
        description="Тип заказов для проверки (CUSTOMER или INTERNAL_BULK)",
    ),
    since_date: Optional[datetime] = Query(
        None,
        description="Дата, с которой искать изменения (ISO format). Если не указана, сравниваются все заказы с их последними снимками.",
    ),
    db: Session = Depends(get_db),
):
    """
    Получить список новых и изменённых заказов.

    Реализует шаг бизнес-процесса "Блок обновления данных" → "Выявить новые и/или измененные ЗП".
    """
    comparison_service = OrderComparisonService(db)

    # Выявляем новые заказы
    new_orders_list = comparison_service.identify_new_orders(
        since_date=since_date,
        order_type=order_type
    )

    # Выявляем изменённые заказы
    changed_orders_list = comparison_service.identify_changed_orders(
        since_date=since_date,
        order_type=order_type
    )

    # Выявляем удалённые заказы
    deleted_snapshots_list = comparison_service.identify_deleted_orders(
        since_date=since_date,
        order_type=order_type
    )

    # Получаем информацию о продуктах для отображения
    product_ids = set()
    for order in new_orders_list + [o[0] for o in changed_orders_list]:
        try:
            product_ids.add(UUID(str(order.product_id)))
        except (ValueError, TypeError):
            pass
    
    # Добавляем product_id из удалённых заказов (из снимков)
    for snapshot in deleted_snapshots_list:
        try:
            product_ids.add(UUID(str(snapshot.product_id)))
        except (ValueError, TypeError):
            pass

    products = db.query(Product).filter(Product.id.in_(product_ids)).all() if product_ids else []
    product_info = {str(p.id): {"name": p.product_name, "code": p.product_code} for p in products}

    # Формируем ответ для новых заказов
    new_orders_data = []
    for order in new_orders_list:
        info = product_info.get(str(order.product_id), {})
        new_orders_data.append(
            OrderChangeInfo(
                order_id=order.id,
                order_number=order.order_number,
                product_id=order.product_id,
                product_name=info.get("name"),
                quantity=order.quantity,
                due_date=order.due_date,
                priority=order.priority,
                is_new=True,
                is_changed=False,
                is_deleted=False,
                changes=None,
            )
        )

    # Формируем ответ для изменённых заказов
    changed_orders_data = []
    for order, snapshot, changes in changed_orders_list:
        info = product_info.get(str(order.product_id), {})
        changed_orders_data.append(
            OrderChangeInfo(
                order_id=order.id,
                order_number=order.order_number,
                product_id=order.product_id,
                product_name=info.get("name"),
                quantity=order.quantity,
                due_date=order.due_date,
                priority=order.priority,
                is_new=False,
                is_changed=True,
                is_deleted=False,
                last_snapshot_date=snapshot.snapshot_date,
                current_updated_at=order.updated_at,
                changes=changes,
            )
        )

    # Формируем ответ для удалённых заказов
    deleted_orders_data = []
    for snapshot in deleted_snapshots_list:
        info = product_info.get(str(snapshot.product_id), {})
        deleted_orders_data.append(
            OrderChangeInfo(
                order_id=snapshot.order_id,  # Может быть старым UUID, если заказ был пересоздан
                order_number=snapshot.order_number,
                product_id=snapshot.product_id,
                product_name=info.get("name"),
                quantity=snapshot.quantity,
                due_date=snapshot.due_date,
                priority=snapshot.priority,
                is_new=False,
                is_changed=False,
                is_deleted=True,
                last_snapshot_date=snapshot.snapshot_date,
                current_updated_at=None,  # Заказа больше нет
                changes=None,
            )
        )

    return OrderChangesListResponse(
        success=True,
        new_orders=new_orders_data,
        changed_orders=changed_orders_data,
        deleted_orders=deleted_orders_data,
        total_new=len(new_orders_data),
        total_changed=len(changed_orders_data),
        total_deleted=len(deleted_orders_data),
    )


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
    "/{order_id}/changes",
    response_model=OrderChangeDetailResponse,
    summary="Get order change details",
    description="Получить детали изменений конкретного заказа (drill-down)",
)
async def get_order_change_details(
    order_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Получить детали изменений конкретного заказа.

    Используется для drill-down в списке изменённых заказов.
    """
    comparison_service = OrderComparisonService(db)
    change_info = comparison_service.get_order_changes(order_id)

    if change_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or has no changes",
        )

    # Дополняем change_info полями, обязательными для OrderChangeInfo
    order = db.get(ManufacturingOrder, order_id)
    if order:
        change_info.setdefault("product_id", str(order.product_id))
        product = db.query(Product).filter(Product.id == UUID(str(order.product_id))).first()
        if product:
            change_info["product_name"] = product.product_name
            change_info["product_code"] = product.product_code
    else:
        # Заказ мог быть удалён — product_id берём из последнего снимка (не передаётся в change_info)
        change_info.setdefault("product_id", "")

    return OrderChangeDetailResponse(
        success=True,
        data=OrderChangeInfo(**change_info),
    )
