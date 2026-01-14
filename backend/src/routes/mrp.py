"""
MRP (Material Requirements Planning) API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime

from backend.src.db.session import get_db
from backend.src.services.mrp_service import MRPService
from backend.src.schemas.mrp import (
    ConsolidateOrdersRequest,
    ConsolidateOrdersResponse,
    ExplodeBOMRequest,
    ExplodeBOMResponse,
    NetRequirementRequest,
    NetRequirementResponse,
    CreateBulkOrderRequest,
    CreateBulkOrderResponse
)

router = APIRouter(prefix="/api/v1/mrp", tags=["MRP"])


@router.post("/consolidate", response_model=ConsolidateOrdersResponse)
def consolidate_orders(
    request: ConsolidateOrdersRequest,
    db: Session = Depends(get_db)
):
    """
    Консолидация клиентских заказов в пределах горизонта планирования.
    
    Группирует заказы по продукту, рассчитывает приоритеты и определяет,
    какие продукты требуют производства.
    
    **Тело запроса:**
    - `horizon_days`: Горизонт планирования в днях (по умолчанию: 30)
    
    **Ответ:**
    - `consolidated_orders`: Список консолидированных планов по продуктам
    - `total_products`: Количество уникальных продуктов
    - `total_orders`: Общее количество заказов
    """
    mrp_service = MRPService(db)
    
    try:
        consolidated = mrp_service.consolidate_orders(
            horizon_days=request.horizon_days
        )
        
        return {
            "success": True,
            "data": {
                "consolidated_orders": consolidated,
                "total_products": len(consolidated),
                "total_orders": sum(c["order_count"] for c in consolidated),
                "planning_horizon_days": request.horizon_days
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка консолидации заказов: {str(e)}"
        )


@router.post("/explode-bom", response_model=ExplodeBOMResponse)
def explode_bom(
    request: ExplodeBOMRequest,
    db: Session = Depends(get_db)
):
    """
    Взрыв BOM для расчёта потребности в материалах.
    
    Рекурсивно обходит дерево спецификации (Bill of Materials) для определения
    всех компонентов, необходимых для производства указанного количества.
    
    **Тело запроса:**
    - `product_id`: Продукт для взрыва
    - `quantity`: Требуемое количество
    
    **Ответ:**
    - `requirements`: Словарь, сопоставляющий product_id количеству
    - `total_components`: Количество уникальных компонентов
    """
    mrp_service = MRPService(db)
    
    try:
        requirements = mrp_service.explode_bom(
            product_id=request.product_id,
            quantity=request.quantity
        )
        
        # Конвертируем UUID ключи в строки для JSON сериализации
        requirements_str = {
            str(prod_id): qty 
            for prod_id, qty in requirements.items()
        }
        
        return {
            "success": True,
            "data": {
                "product_id": str(request.product_id),
                "quantity": request.quantity,
                "requirements": requirements_str,
                "total_components": len(requirements)
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка взрыва BOM: {str(e)}"
        )


@router.post("/net-requirement", response_model=NetRequirementResponse)
def calculate_net_requirement(
    request: NetRequirementRequest,
    db: Session = Depends(get_db)
):
    """
    Расчёт нетто-потребности (валовая - доступный запас).
    
    **Тело запроса:**
    - `product_id`: Продукт для проверки
    - `gross_requirement`: Валовая потребность
    
    **Ответ:**
    - `net_requirement`: Нетто-потребность (валовая - доступный)
    - `available_stock`: Доступный запас
    - `needs_production`: Флаг необходимости производства
    """
    mrp_service = MRPService(db)
    
    try:
        net_req = mrp_service.calculate_net_requirement(
            product_id=request.product_id,
            gross_requirement=request.gross_requirement
        )
        
        available = request.gross_requirement - net_req
        
        return {
            "success": True,
            "data": {
                "product_id": str(request.product_id),
                "gross_requirement": request.gross_requirement,
                "available_stock": available,
                "net_requirement": net_req,
                "needs_production": net_req > 0
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка расчёта нетто-потребности: {str(e)}"
        )


@router.post("/create-bulk-order", response_model=CreateBulkOrderResponse)
def create_bulk_order(
    request: CreateBulkOrderRequest,
    db: Session = Depends(get_db)
):
    """
    Создание зависимого INTERNAL_BULK заказа на варку массы.
    
    **Тело запроса:**
    - `parent_order_id`: Родительский заказ (опционально, для зависимых заказов)
    - `bulk_product_id`: BULK продукт для варки
    - `quantity_kg`: Количество (будет округлено до батча)
    - `due_date`: Дата выполнения
    
    **Ответ:**
    - `order`: Созданный производственный заказ
    - `rounded_quantity`: Фактическое количество после округления до батча
    """
    mrp_service = MRPService(db)
    
    try:
        # Округляем до батча
        rounded_qty = mrp_service.round_to_batch(
            product_id=request.bulk_product_id,
            net_requirement_kg=request.quantity_kg
        )
        
        # Создаём заказ
        order = mrp_service.create_dependent_bulk_order(
            bulk_product_id=request.bulk_product_id,
            quantity_kg=rounded_qty,
            due_date=request.due_date,
            parent_order_id=request.parent_order_id  # Опционально
        )
        
        return {
            "success": True,
            "data": {
                "order": {
                    "id": str(order.id),
                    "order_number": order.order_number,
                    "product_id": order.product_id,
                    "quantity": float(order.quantity),
                    "status": order.status.value,
                    "order_type": order.order_type,
                    "parent_order_id": str(order.parent_order_id) if order.parent_order_id else None,
                    "due_date": order.due_date
                },
                "rounded_quantity": rounded_qty,
                "original_quantity": request.quantity_kg
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания заказа на варку: {str(e)}"
        )
