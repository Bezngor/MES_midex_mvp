"""
MRP (Material Requirements Planning) схемы.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime


# ============================================================================
# Консолидация заказов
# ============================================================================

class ConsolidateOrdersRequest(BaseModel):
    """Схема запроса для консолидации заказов."""
    horizon_days: int = Field(default=30, ge=1, le=365, description="Горизонт планирования в днях")


class ConsolidatedOrderPlan(BaseModel):
    """Один консолидированный план заказа."""
    product_id: UUID
    product_code: str
    product_name: str
    total_quantity: float
    priority: Optional[str] = None
    earliest_due_date: Optional[datetime] = None
    latest_due_date: Optional[datetime] = None
    source_orders: List[UUID]
    order_count: int


class ConsolidateOrdersResponse(BaseModel):
    """Схема ответа для консолидации заказов."""
    success: bool
    data: Dict


# ============================================================================
# Взрыв BOM
# ============================================================================

class ExplodeBOMRequest(BaseModel):
    """Схема запроса для взрыва BOM."""
    product_id: UUID = Field(..., description="Продукт для взрыва")
    quantity: float = Field(..., gt=0, description="Требуемое количество")


class ExplodeBOMResponse(BaseModel):
    """Схема ответа для взрыва BOM."""
    success: bool
    data: Dict


# ============================================================================
# Нетто-потребность
# ============================================================================

class NetRequirementRequest(BaseModel):
    """Схема запроса для расчёта нетто-потребности."""
    product_id: UUID
    gross_requirement: float = Field(..., gt=0)


class NetRequirementResponse(BaseModel):
    """Схема ответа для расчёта нетто-потребности."""
    success: bool
    data: Dict


# ============================================================================
# Создание заказа на варку
# ============================================================================

class CreateBulkOrderRequest(BaseModel):
    """Схема запроса для создания заказа на варку."""
    parent_order_id: Optional[UUID] = Field(default=None, description="Родительский заказ (опционально, для зависимых заказов)")
    bulk_product_id: UUID
    quantity_kg: float = Field(..., gt=0)
    due_date: datetime


class CreateBulkOrderResponse(BaseModel):
    """Схема ответа для создания заказа на варку."""
    success: bool
    data: Dict
