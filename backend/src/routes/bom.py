"""
API-роуты для спецификаций (Bill of Material).
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.src.models.bill_of_material import BillOfMaterial
from backend.src.schemas.bom import BOMCreate, BOMResponse

router = APIRouter(prefix="/api/v1/bill-of-materials", tags=["bill-of-materials"])


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Создать строку спецификации",
)
async def create_bom(
    payload: BOMCreate,
    db: Session = Depends(get_db),
) -> dict:
    """Создать строку спецификации.

    Гарантируется уникальность пары (parent_product_id, child_product_id) на уровне БД.
    """
    bom = BillOfMaterial(
        parent_product_id=payload.parent_product_id,
        child_product_id=payload.child_product_id,
        quantity=payload.quantity,
        unit=payload.unit,
        sequence=payload.sequence,
    )
    try:
        db.add(bom)
        db.commit()
        db.refresh(bom)
    except Exception as exc:  # pragma: no cover - общее перехватывание для ответов API
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Не удалось создать строку спецификации: {exc}",
        ) from exc

    return {"success": True, "data": BOMResponse.model_validate(bom)}


@router.get(
    "",
    response_model=dict,
    summary="Список строк спецификаций",
)
async def list_bom(
    parent_product_id: Optional[UUID] = Query(
        default=None,
        description="Фильтр по родительскому продукту.",
    ),
    child_product_id: Optional[UUID] = Query(
        default=None,
        description="Фильтр по дочернему продукту.",
    ),
    db: Session = Depends(get_db),
) -> dict:
    """Получить список строк спецификаций с возможной фильтрацией."""
    query = db.query(BillOfMaterial)
    if parent_product_id is not None:
        query = query.filter(BillOfMaterial.parent_product_id == parent_product_id)
    if child_product_id is not None:
        query = query.filter(BillOfMaterial.child_product_id == child_product_id)

    items = query.all()
    return {
        "success": True,
        "data": [BOMResponse.model_validate(item) for item in items],
    }


@router.get(
    "/{bom_id}",
    response_model=dict,
    summary="Получить строку спецификации по ID",
)
async def get_bom(
    bom_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    """Получить строку спецификации по UUID."""
    bom = db.query(BillOfMaterial).filter(BillOfMaterial.id == bom_id).first()
    if bom is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Строка спецификации не найдена.",
        )

    return {"success": True, "data": BOMResponse.model_validate(bom)}


@router.patch(
    "/{bom_id}",
    response_model=dict,
    summary="Обновить строку спецификации",
)
async def update_bom(
    bom_id: UUID,
    payload: BOMCreate,
    db: Session = Depends(get_db),
) -> dict:
    """Обновить данные строки спецификации.

    Для MVP используем ту же схему, что и для создания.
    """
    bom = db.query(BillOfMaterial).filter(BillOfMaterial.id == bom_id).first()
    if bom is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Строка спецификации не найдена.",
        )

    data = payload.model_dump()
    for field, value in data.items():
        setattr(bom, field, value)

    try:
        db.add(bom)
        db.commit()
        db.refresh(bom)
    except Exception as exc:  # pragma: no cover
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Не удалось обновить строку спецификации: {exc}",
        ) from exc

    return {"success": True, "data": BOMResponse.model_validate(bom)}


@router.delete(
    "/{bom_id}",
    response_model=dict,
    summary="Удалить строку спецификации",
)
async def delete_bom(
    bom_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    """Удалить строку спецификации по UUID."""
    bom = db.query(BillOfMaterial).filter(BillOfMaterial.id == bom_id).first()
    if bom is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Строка спецификации не найдена.",
        )

    db.delete(bom)
    db.commit()

    return {"success": True, "data": None}


