"""
Pydantic-схемы для API выявления изменений заказов.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any


class OrderChangeDetail(BaseModel):
    """Детали изменения одного поля заказа."""

    field: str = Field(..., description="Название поля")
    old_value: Any = Field(..., description="Старое значение")
    new_value: Any = Field(..., description="Новое значение")


class OrderChangeInfo(BaseModel):
    """Информация об изменениях заказа."""

    order_id: Optional[UUID] = Field(None, description="ID заказа (может быть None для удалённых заказов)")
    order_number: str
    product_id: str
    product_name: Optional[str] = None
    is_new: bool = Field(..., description="Является ли заказ новым (нет снимков)")
    is_changed: bool = Field(default=False, description="Был ли заказ изменён")
    is_deleted: bool = Field(default=False, description="Был ли заказ удалён (есть в снимках, но отсутствует в таблице)")
    last_snapshot_date: Optional[datetime] = None
    current_updated_at: Optional[datetime] = None
    changes: Optional[Dict[str, tuple]] = Field(None, description="Словарь изменений: {поле: (старое, новое)}")

    model_config = ConfigDict(from_attributes=True)


class OrderChangesListResponse(BaseModel):
    """Ответ API со списком новых, изменённых и удалённых заказов."""

    success: bool = True
    new_orders: List[OrderChangeInfo] = Field(default_factory=list, description="Список новых заказов")
    changed_orders: List[OrderChangeInfo] = Field(default_factory=list, description="Список изменённых заказов")
    deleted_orders: List[OrderChangeInfo] = Field(default_factory=list, description="Список удалённых заказов")
    total_new: int = Field(..., description="Общее количество новых заказов")
    total_changed: int = Field(..., description="Общее количество изменённых заказов")
    total_deleted: int = Field(..., description="Общее количество удалённых заказов")


class OrderChangeDetailResponse(BaseModel):
    """Ответ API с деталями изменений конкретного заказа."""

    success: bool = True
    data: Optional[OrderChangeInfo] = None
