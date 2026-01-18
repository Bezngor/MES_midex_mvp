"""
API-роуты для мощностей рабочих центров по продукту.
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.core.models.work_center_capacity import WorkCenterCapacity
from backend.core.schemas.work_center_capacity import CapacityCreate, CapacityResponse

router = APIRouter(
    prefix="/api/v1/work-center-capacities",
    tags=["work-center-capacities"],
)


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Создать запись мощности РЦ по продукту",
)
async def create_capacity(
    payload: CapacityCreate,
    db: Session = Depends(get_db),
) -> dict:
    """Создать запись мощности рабочего центра по продукту."""
    existing = (
        db.query(WorkCenterCapacity)
        .filter(
            WorkCenterCapacity.work_center_id == payload.work_center_id,
            WorkCenterCapacity.product_id == payload.product_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Мощность для данной пары (work_center_id, product_id) уже существует.",
        )

    capacity = WorkCenterCapacity(
        work_center_id=payload.work_center_id,
        product_id=payload.product_id,
        capacity_per_shift=payload.capacity_per_shift,
        unit=payload.unit,
    )
    db.add(capacity)
    db.commit()
    db.refresh(capacity)

    return {"success": True, "data": CapacityResponse.model_validate(capacity)}


@router.get(
    "",
    response_model=dict,
    summary="Список мощностей РЦ по продуктам",
)
async def list_capacities(
    work_center_id: Optional[UUID] = Query(
        default=None,
        description="Фильтр по рабочему центру.",
    ),
    product_id: Optional[UUID] = Query(
        default=None,
        description="Фильтр по продукту.",
    ),
    db: Session = Depends(get_db),
) -> dict:
    """Получить список мощностей по фильтрам."""
    query = db.query(WorkCenterCapacity)
    if work_center_id is not None:
        query = query.filter(WorkCenterCapacity.work_center_id == work_center_id)
    if product_id is not None:
        query = query.filter(WorkCenterCapacity.product_id == product_id)

    items = query.all()
    return {
        "success": True,
        "data": [CapacityResponse.model_validate(item) for item in items],
    }


@router.get(
    "/{capacity_id}",
    response_model=dict,
    summary="Получить запись мощности по ID",
)
async def get_capacity(
    capacity_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    """Получить запись мощности по UUID."""
    capacity = db.query(WorkCenterCapacity).filter(WorkCenterCapacity.id == capacity_id).first()
    if capacity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись мощности не найдена.",
        )

    return {"success": True, "data": CapacityResponse.model_validate(capacity)}


@router.patch(
    "/{capacity_id}",
    response_model=dict,
    summary="Обновить запись мощности",
)
async def update_capacity(
    capacity_id: UUID,
    payload: CapacityCreate,
    db: Session = Depends(get_db),
) -> dict:
    """Обновить запись мощности рабочего центра по продукту.

    Для MVP используем ту же схему, что и для создания.
    """
    capacity = db.query(WorkCenterCapacity).filter(WorkCenterCapacity.id == capacity_id).first()
    if capacity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись мощности не найдена.",
        )

    data = payload.model_dump()
    for field, value in data.items():
        setattr(capacity, field, value)

    db.add(capacity)
    db.commit()
    db.refresh(capacity)

    return {"success": True, "data": CapacityResponse.model_validate(capacity)}


@router.delete(
    "/{capacity_id}",
    response_model=dict,
    summary="Удалить запись мощности",
)
async def delete_capacity(
    capacity_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    """Удалить запись мощности по UUID."""
    capacity = db.query(WorkCenterCapacity).filter(WorkCenterCapacity.id == capacity_id).first()
    if capacity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись мощности не найдена.",
        )

    db.delete(capacity)
    db.commit()

    return {"success": True, "data": None}


