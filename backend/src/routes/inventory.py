"""
API-роуты для управления остатками (InventoryBalance).
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from backend.src.db.session import get_db
from backend.src.models.inventory_balance import InventoryBalance
from backend.src.models.enums import ProductStatus
from backend.src.schemas.inventory import InventoryAdjust, InventoryResponse

router = APIRouter(prefix="/api/v1/inventory", tags=["inventory"])


@router.get(
    "",
    response_model=dict,
    summary="Список остатков",
)
async def list_inventory(
    product_id: Optional[UUID] = Query(default=None, description="Фильтр по продукту."),
    location: Optional[str] = Query(default=None, description="Фильтр по локации."),
    product_status: Optional[ProductStatus] = Query(
        default=None,
        description="Фильтр по статусу продукта (FINISHED/SEMI_FINISHED).",
    ),
    db: Session = Depends(get_db),
) -> dict:
    """Получить список остатков с базовой фильтрацией."""
    query = db.query(InventoryBalance).options(
        # Жадная загрузка связанного продукта, чтобы фронтенд мог отобразить имя продукта
        joinedload(InventoryBalance.product)
    )
    if product_id is not None:
        query = query.filter(InventoryBalance.product_id == product_id)
    if location is not None:
        query = query.filter(InventoryBalance.location == location)
    if product_status is not None:
        query = query.filter(InventoryBalance.product_status == product_status.value)

    items = query.all()
    return {
        "success": True,
        "data": [InventoryResponse.model_validate(item) for item in items],
    }


@router.get(
    "/{inventory_id}",
    response_model=dict,
    summary="Получить запись остатка по ID",
)
async def get_inventory(
    inventory_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    """Получить запись остатка по UUID."""
    inv = db.query(InventoryBalance).filter(InventoryBalance.id == inventory_id).first()
    if inv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись остатка не найдена.",
        )

    return {"success": True, "data": InventoryResponse.model_validate(inv)}


@router.post(
    "/adjust",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Скорректировать остаток",
    description="Выполняет upsert по (product_id, location, product_status) и изменяет количество/резерв.",
)
async def adjust_inventory(
    payload: InventoryAdjust,
    db: Session = Depends(get_db),
) -> dict:
    """Скорректировать остаток по продукту, локации и статусу.

    - Если запись отсутствует, создаётся новая.
    - Количество и резерв изменяются на переданные дельты.
    - Валидация: quantity и reserved_quantity не могут быть отрицательными.
    """
    inv = (
        db.query(InventoryBalance)
        .filter(
            InventoryBalance.product_id == payload.product_id,
            InventoryBalance.location == payload.location,
            InventoryBalance.product_status == payload.product_status.value,
        )
        .first()
    )

    if inv is None:
        inv = InventoryBalance(
            product_id=payload.product_id,
            location=payload.location,
            quantity=0,
            unit=payload.unit,
            product_status=payload.product_status.value,
            production_date=payload.production_date,
            expiry_date=payload.expiry_date,
            reserved_quantity=0,
        )
        db.add(inv)
        db.flush()

    # Устанавливаем количество: либо абсолютное значение, либо дельта
    if payload.quantity is not None:
        inv.quantity = payload.quantity
    elif payload.quantity_delta is not None:
        inv.quantity = (inv.quantity or 0) + payload.quantity_delta
    
    # Устанавливаем резерв: либо абсолютное значение, либо дельта
    if payload.reserved_quantity is not None:
        inv.reserved_quantity = payload.reserved_quantity
    elif payload.reserved_delta is not None:
        inv.reserved_quantity = (inv.reserved_quantity or 0) + payload.reserved_delta

    if inv.quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Результирующее количество не может быть отрицательным.",
        )
    if inv.reserved_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Результирующий резерв не может быть отрицательным.",
        )
    if inv.reserved_quantity > inv.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Резерв не может превышать общее количество.",
        )

    # Обновляем даты, если они переданы
    if payload.production_date is not None:
        inv.production_date = payload.production_date
    if payload.expiry_date is not None:
        inv.expiry_date = payload.expiry_date

    db.add(inv)
    db.commit()
    db.refresh(inv)

    return {"success": True, "data": InventoryResponse.model_validate(inv)}


@router.delete(
    "/{inventory_id}",
    response_model=dict,
    summary="Удалить запись остатка",
)
async def delete_inventory(
    inventory_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    """Удалить запись остатка по UUID."""
    inv = db.query(InventoryBalance).filter(InventoryBalance.id == inventory_id).first()
    if inv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись остатка не найдена.",
        )

    db.delete(inv)
    db.commit()

    return {"success": True, "data": None}


