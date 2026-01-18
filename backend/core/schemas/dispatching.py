"""
Схемы для диспетчеризации и планирования.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime


# ============================================================================
# Выпуск заказа
# ============================================================================

class ReleaseOrderRequest(BaseModel):
    """Схема запроса для выпуска заказа."""
    order_id: UUID = Field(..., description="ID производственного заказа")
    release_date: Optional[datetime] = Field(None, description="Дата выпуска (по умолчанию: сейчас)")


class ReleaseOrderResponse(BaseModel):
    """Схема ответа для выпуска заказа."""
    success: bool
    data: Dict


# ============================================================================
# Диспетчеризация задачи
# ============================================================================

class DispatchTaskRequest(BaseModel):
    """Схема запроса для диспетчеризации задачи."""
    task_id: UUID = Field(..., description="ID задачи")
    work_center_id: UUID = Field(..., description="ID рабочего центра")
    scheduled_start: Optional[datetime] = Field(None, description="Запланированное время начала")


class DispatchTaskResponse(BaseModel):
    """Схема ответа для диспетчеризации задачи."""
    success: bool
    data: Dict


# ============================================================================
# Расписание
# ============================================================================

class ScheduleResponse(BaseModel):
    """Схема ответа для расписания."""
    success: bool
    data: Dict


# ============================================================================
# Загрузка рабочего центра
# ============================================================================

class WorkCenterLoadResponse(BaseModel):
    """Схема ответа для загрузки рабочего центра."""
    success: bool
    data: Dict


# ============================================================================
# Данные Ганта
# ============================================================================

class GanttDataResponse(BaseModel):
    """Схема ответа для данных диаграммы Ганта."""
    success: bool
    data: Dict
