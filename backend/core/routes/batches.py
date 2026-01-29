"""
API-роуты для управления батчами (Batch).
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from backend.src.db.session import get_db
from backend.core.models.batch import Batch
from backend.core.models.enums import BatchStatus
from backend.core.schemas.batch import BatchCreate, BatchUpdate, BatchResponse

# Роутер для действий start/complete — подключается в main.py ПЕРВЫМ, чтобы пути
# /api/v1/batches/start/{id} и /complete/{id} гарантированно сопоставлялись до общих /{batch_id}.
router_actions = APIRouter(prefix="/api/v1/batches", tags=["batches"])

router = APIRouter(prefix="/api/v1/batches", tags=["batches"])


def _ensure_product_loaded(batch: Batch) -> None:
    """Обеспечивает загрузку связи product (для product_name в ответе)."""
    _ = batch.product


def _batch_to_response(batch: Batch) -> dict:
    """Сериализует батч в ответ с product_name для UI."""
    data = BatchResponse.model_validate(batch).model_dump()
    data["product_name"] = batch.product.product_name if batch.product else None
    return data


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
    _ensure_product_loaded(batch)

    return {"success": True, "data": _batch_to_response(batch)}


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

    items = query.options(joinedload(Batch.product)).all()
    return {
        "success": True,
        "data": [_batch_to_response(item) for item in items],
    }


@router_actions.patch(
    "/start/{batch_id}",
    response_model=dict,
    summary="Запустить батч",
)
async def start_batch(
    batch_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    """Перевести батч в статус IN_PROGRESS и зафиксировать started_at."""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Батч не найден.",
        )
    if batch.status != BatchStatus.PLANNED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Запуск возможен только для батча в статусе PLANNED. Текущий статус: {batch.status}.",
        )
    batch.status = BatchStatus.IN_PROGRESS.value
    batch.started_at = datetime.utcnow()
    db.add(batch)
    db.commit()
    db.refresh(batch)
    _ensure_product_loaded(batch)
    return {"success": True, "data": _batch_to_response(batch)}


@router_actions.patch(
    "/complete/{batch_id}",
    response_model=dict,
    summary="Завершить батч",
)
async def complete_batch(
    batch_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    """Перевести батч в статус COMPLETED и зафиксировать completed_at."""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if batch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Батч не найден.",
        )
    if batch.status != BatchStatus.IN_PROGRESS.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Завершение возможно только для батча в статусе IN_PROGRESS. Текущий статус: {batch.status}.",
        )
    batch.status = BatchStatus.COMPLETED.value
    batch.completed_at = datetime.utcnow()
    db.add(batch)
    db.commit()
    db.refresh(batch)
    _ensure_product_loaded(batch)
    return {"success": True, "data": _batch_to_response(batch)}


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
    _ensure_product_loaded(batch)
    return {"success": True, "data": _batch_to_response(batch)}


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
    _ensure_product_loaded(batch)
    return {"success": True, "data": _batch_to_response(batch)}


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


