"""
API-роуты для управления батчами (Batch).
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.src.models.batch import Batch
from backend.src.models.enums import BatchStatus
from backend.src.schemas.batch import BatchCreate, BatchUpdate, BatchResponse

router = APIRouter(prefix="/api/v1/batches", tags=["batches"])


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Создать батч",
)
async def create_batch(
    payload: BatchCreate,
    db: Session = Depends(get_db),
) -> dict:
    """Создать новый батч.

    Проверяет уникальность `batch_number`. Если `batch_number` не указан,
    генерирует его автоматически в формате BATCH-YYYYMMDD-HHMMSS-UUID.
    """
    # Генерируем batch_number, если не указан
    batch_number = payload.batch_number
    if not batch_number:
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        batch_number = f"BATCH-{timestamp}-{uuid4().hex[:8].upper()}"
    
    # Проверяем уникальность batch_number
    existing = db.query(Batch).filter(Batch.batch_number == batch_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Батч с таким batch_number уже существует.",
        )

    batch = Batch(
        batch_number=batch_number,
        product_id=payload.product_id,
        quantity_kg=payload.quantity_kg,
        status=payload.status.value,
        work_center_id=payload.work_center_id,
        operator_id=payload.operator_id,
        planned_start=payload.planned_start,
        storage_location_id=payload.storage_location_id,
        parent_order_id=payload.parent_order_id,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    return {"success": True, "data": BatchResponse.model_validate(batch)}


@router.get(
    "",
    response_model=dict,
    summary="Список батчей",
)
async def list_batches(
    status_filter: Optional[BatchStatus] = Query(
        default=None,
        alias="status",
        description="Фильтр по статусу батча.",
    ),
    product_id: Optional[UUID] = Query(default=None, description="Фильтр по продукту."),
    parent_order_id: Optional[UUID] = Query(default=None, description="Фильтр по родительскому заказу."),
    db: Session = Depends(get_db),
) -> dict:
    """Получить список батчей с фильтрацией по статусу, продукту и заказу."""
    query = db.query(Batch)
    if status_filter is not None:
        query = query.filter(Batch.status == status_filter.value)
    if product_id is not None:
        query = query.filter(Batch.product_id == product_id)
    if parent_order_id is not None:
        query = query.filter(Batch.parent_order_id == parent_order_id)

    items = query.all()
    return {
        "success": True,
        "data": [BatchResponse.model_validate(item) for item in items],
    }


@router.get(
    "/{batch_id}",
    response_model=dict,
    summary="Получить батч по ID",
)
async def get_batch(
    batch_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    """Получить батч по UUID."""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Батч не найден.",
        )

    return {"success": True, "data": BatchResponse.model_validate(batch)}


@router.patch(
    "/{batch_id}",
    response_model=dict,
    summary="Обновить батч",
)
async def update_batch(
    batch_id: UUID,
    payload: BatchUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """Частично обновить данные батча (статус, времена, оператор и т.п.)."""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Батч не найден.",
        )

    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"] is not None:
        data["status"] = data["status"].value

    for field, value in data.items():
        setattr(batch, field, value)

    db.add(batch)
    db.commit()
    db.refresh(batch)

    return {"success": True, "data": BatchResponse.model_validate(batch)}


@router.delete(
    "/{batch_id}",
    response_model=dict,
    summary="Удалить батч",
)
async def delete_batch(
    batch_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    """Удалить батч по UUID."""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Батч не найден.",
        )

    db.delete(batch)
    db.commit()

    return {"success": True, "data": None}


