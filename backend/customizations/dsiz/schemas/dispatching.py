"""
DSIZ Dispatching API Schemas.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime


class DispatchRunRequest(BaseModel):
    """Схема запроса для запуска preview диспетчеризации."""
    manufacturing_order_ids: List[UUID] = Field(
        ..., 
        description="Список ID производственных заказов для preview"
    )
    work_center_id: Optional[UUID] = Field(
        None,
        description="ID рабочего центра (опционально, для фильтрации)"
    )


class GanttTaskPreview(BaseModel):
    """Задача в preview Gantt."""
    task_id: str = Field(..., description="ID задачи")
    order_id: str = Field(..., description="ID заказа")
    work_center_id: str = Field(..., description="ID рабочего центра")
    work_center_name: str = Field(..., description="Название рабочего центра")
    task_start: datetime = Field(..., description="Время начала задачи")
    task_end: datetime = Field(..., description="Время окончания задачи")
    duration_hours: float = Field(..., description="Длительность в часах")
    changeover_minutes: int = Field(..., description="Время переналадки в минутах")
    status: str = Field(..., description="Статус задачи")
    priority: str = Field(..., description="Приоритет заказа")


class ConflictInfo(BaseModel):
    """Информация о конфликте в расписании."""
    task_id: str = Field(..., description="ID задачи с конфликтом")
    conflict_with: str = Field(..., description="ID задачи, с которой конфликт")
    work_center_id: str = Field(..., description="ID рабочего центра")
    overlap_start: datetime = Field(..., description="Начало пересечения")
    overlap_end: datetime = Field(..., description="Конец пересечения")


class DispatchPreviewResponse(BaseModel):
    """Схема ответа для preview диспетчеризации."""
    success: bool = Field(..., description="Успешность выполнения")
    data: Dict = Field(
        ...,
        description="Данные preview с gantt_preview и conflicts"
    )


class WorkCenterLoadResponse(BaseModel):
    """Схема ответа для загрузки рабочего центра."""
    success: bool = Field(..., description="Успешность выполнения")
    data: Dict = Field(
        ...,
        description="Данные о загрузке рабочего центра"
    )
