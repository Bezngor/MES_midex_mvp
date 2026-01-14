"""
API-роуты для управления продуктами (Product).
"""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.src.db.session import get_db
from backend.src.models.product import Product
from backend.src.models.enums import ProductType
from backend.src.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/api/v1/products", tags=["products"])


@router.post(
    "",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Создать продукт",
    description="Создаёт новый продукт (сырьё, bulk, упаковка или готовая продукция).",
)
async def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
) -> dict:
    """Создать новый продукт.

    Проверяет уникальность `product_code`.
    """
    existing = db.query(Product).filter(Product.product_code == payload.product_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Продукт с таким product_code уже существует.",
        )

    product = Product(
        product_code=payload.product_code,
        product_name=payload.product_name,
        product_type=payload.product_type.value,
        unit_of_measure=payload.unit_of_measure,
        min_batch_size_kg=payload.min_batch_size_kg,
        batch_size_step_kg=payload.batch_size_step_kg,
        shelf_life_days=payload.shelf_life_days,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    return {"success": True, "data": ProductResponse.model_validate(product)}


@router.get(
    "",
    response_model=dict,
    summary="Список продуктов",
    description="Возвращает список продуктов с опциональной фильтрацией по типу.",
)
async def list_products(
    product_type: Optional[ProductType] = Query(
        default=None,
        description="Фильтр по типу продукта.",
    ),
    skip: int = Query(0, ge=0, description="Смещение."),
    limit: int = Query(100, ge=1, le=200, description="Максимальное количество записей."),
    db: Session = Depends(get_db),
) -> dict:
    """Получить список продуктов с фильтрацией по типу."""
    query = db.query(Product)
    if product_type is not None:
        query = query.filter(Product.product_type == product_type.value)

    items = query.offset(skip).limit(limit).all()
    return {
        "success": True,
        "data": [ProductResponse.model_validate(item) for item in items],
    }


@router.get(
    "/{product_id}",
    response_model=dict,
    summary="Получить продукт по ID",
)
async def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    """Получить продукт по его UUID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Продукт не найден.",
        )

    return {"success": True, "data": ProductResponse.model_validate(product)}


@router.patch(
    "/{product_id}",
    response_model=dict,
    summary="Обновить продукт",
)
async def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """Частично обновить данные продукта."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Продукт не найден.",
        )

    update_data = payload.model_dump(exclude_unset=True)
    # Особая обработка product_type (enum -> str)
    if "product_type" in update_data and update_data["product_type"] is not None:
        update_data["product_type"] = update_data["product_type"].value

    for field, value in update_data.items():
        setattr(product, field, value)

    db.add(product)
    db.commit()
    db.refresh(product)

    return {"success": True, "data": ProductResponse.model_validate(product)}


@router.delete(
    "/{product_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Удалить продукт",
)
async def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    """Удалить продукт по UUID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Продукт не найден.",
        )

    db.delete(product)
    db.commit()

    return {"success": True, "data": None}


