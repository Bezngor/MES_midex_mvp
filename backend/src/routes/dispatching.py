"""
API эндпоинты для диспетчеризации и планирования.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime

from backend.src.db.session import get_db
from backend.src.services.dispatching_service import DispatchingService
from backend.src.schemas.dispatching import (
    ReleaseOrderRequest,
    ReleaseOrderResponse,
    DispatchTaskRequest,
    DispatchTaskResponse,
    ScheduleResponse,
    WorkCenterLoadResponse,
    GanttDataResponse
)

router = APIRouter(prefix="/api/v1/dispatching", tags=["Dispatching"])


@router.post("/release-order", response_model=ReleaseOrderResponse)
async def release_order(
    request: ReleaseOrderRequest,
    db: Session = Depends(get_db)
):
    """
    Выпустить заказ в производство (PLANNED → RELEASED).

    Создаёт записи ProductionTask и меняет статус заказа.

    **Тело запроса:**
    - `order_id`: ID производственного заказа
    - `release_date`: Дата выпуска (опционально, по умолчанию: сейчас)

    **Ответ:**
    - `order`: Обновлённые данные заказа
    - `tasks_created`: Количество созданных задач
    """
    service = DispatchingService(db)

    try:
        order = service.release_order(
            order_id=request.order_id,
            release_date=request.release_date
        )

        # Подсчитываем задачи
        tasks_count = len([t for t in order.production_tasks if t.status.value == "QUEUED"])

        return {
            "success": True,
            "data": {
                "order": {
                    "id": order.id,
                    "order_number": order.order_number,
                    "status": order.status.value,
                    "updated_at": order.updated_at
                },
                "tasks_created": tasks_count
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/dispatch-task", response_model=DispatchTaskResponse)
async def dispatch_task(
    request: DispatchTaskRequest,
    db: Session = Depends(get_db)
):
    """
    Диспетчеризовать задачу на рабочий центр.

    **Тело запроса:**
    - `task_id`: ID задачи
    - `work_center_id`: ID рабочего центра
    - `scheduled_start`: Запланированное время начала (опционально)

    **Ответ:**
    - `task`: Обновлённые данные задачи
    """
    service = DispatchingService(db)

    try:
        task = service.dispatch_task(
            task_id=request.task_id,
            work_center_id=request.work_center_id,
            scheduled_start=request.scheduled_start
        )

        return {
            "success": True,
            "data": {
                "task": {
                    "id": task.id,
                    "task_name": task.route_operation.operation_name if task.route_operation else "Задача",
                    "work_center_id": task.work_center_id,
                    "status": task.status.value,
                    "scheduled_start": task.started_at,
                    "scheduled_end": task.completed_at
                }
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/schedule", response_model=ScheduleResponse)
async def get_schedule(
    work_center_id: Optional[UUID] = Query(None, description="Фильтр по рабочему центру"),
    horizon_days: int = Query(7, ge=1, le=30, description="Горизонт планирования в днях"),
    db: Session = Depends(get_db)
):
    """
    Получить расписание задач для рабочего центра(ов).

    **Параметры запроса:**
    - `work_center_id`: Фильтр по конкретному рабочему центру (опционально)
    - `horizon_days`: Горизонт планирования в днях (по умолчанию: 7)

    **Ответ:**
    - `schedule`: Список запланированных задач
    - `total_tasks`: Общее количество задач
    """
    service = DispatchingService(db)

    schedule = service.schedule_tasks(
        work_center_id=work_center_id,
        horizon_days=horizon_days
    )

    return {
        "success": True,
        "data": {
            "schedule": schedule,
            "total_tasks": len(schedule),
            "horizon_days": horizon_days
        }
    }


@router.get("/work-center-load/{work_center_id}", response_model=WorkCenterLoadResponse)
async def get_work_center_load(
    work_center_id: UUID,
    date: Optional[datetime] = Query(None, description="Дата для расчёта загрузки"),
    db: Session = Depends(get_db)
):
    """
    Рассчитать загрузку рабочего центра (процент использования).

    **Параметры пути:**
    - `work_center_id`: ID рабочего центра

    **Параметры запроса:**
    - `date`: Дата для расчёта (опционально, по умолчанию: сегодня)

    **Ответ:**
    - `load_percentage`: Процент использования (0-100+)
    - `status`: "Available", "Busy", "Overloaded"
    """
    service = DispatchingService(db)

    load = service.calculate_work_center_load(
        work_center_id=work_center_id,
        date=date
    )

    # Определяем статус
    if load < 70:
        load_status = "Available"
    elif load < 100:
        load_status = "Busy"
    else:
        load_status = "Overloaded"

    return {
        "success": True,
        "data": {
            "work_center_id": work_center_id,
            "load_percentage": load,
            "status": load_status,
            "date": date or datetime.utcnow()
        }
    }


@router.get("/gantt-data", response_model=GanttDataResponse)
async def get_gantt_data(
    work_center_id: Optional[UUID] = Query(None, description="Фильтр по рабочему центру"),
    start_date: Optional[datetime] = Query(None, description="Дата начала"),
    end_date: Optional[datetime] = Query(None, description="Дата окончания"),
    db: Session = Depends(get_db)
):
    """
    Получить данные для диаграммы Ганта для визуализации.

    **Параметры запроса:**
    - `work_center_id`: Фильтр по рабочему центру (опционально)
    - `start_date`: Дата начала (опционально, по умолчанию: сегодня)
    - `end_date`: Дата окончания (опционально, по умолчанию: +7 дней)

    **Ответ:**
    - `work_centers`: Массив рабочих центров с задачами
    - `start_date`: Дата начала диаграммы
    - `end_date`: Дата окончания диаграммы
    """
    service = DispatchingService(db)

    gantt_data = service.get_gantt_data(
        work_center_id=work_center_id,
        start_date=start_date,
        end_date=end_date
    )

    return {
        "success": True,
        "data": gantt_data
    }
