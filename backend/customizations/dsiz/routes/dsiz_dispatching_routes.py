"""
DSIZ Dispatching API Routes.

Эндпоинты для DSIZ-специфичной диспетчеризации с учётом:
- Фильтрации по product_work_center_routing
- Времени переналадки (changeover time)
- Доступности персонала
- Приоритетной сортировки
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from backend.src.db.session import get_db
from backend.core.services.dispatching_service import DispatchingService
from backend.customizations.dsiz.services.dsiz_dispatching_service import DSIZDispatchingService
from backend.customizations.dsiz.schemas.dispatching import (
    DispatchRunRequest,
    DispatchPreviewResponse,
    WorkCenterLoadResponse,
)

router = APIRouter(prefix="/dsiz/dispatching", tags=["DSIZ Dispatching"])


def get_dsiz_dispatching_service(db: Session = Depends(get_db)) -> DSIZDispatchingService:
    """
    Dependency для получения DSIZDispatchingService.
    
    Args:
        db: Сессия базы данных
    
    Returns:
        DSIZDispatchingService экземпляр
    """
    return DSIZDispatchingService(db)


@router.post("/run", response_model=DispatchPreviewResponse)
async def run_dispatch_preview(
    request: DispatchRunRequest,
    db: Session = Depends(get_db),
    service: DSIZDispatchingService = Depends(get_dsiz_dispatching_service)
) -> DispatchPreviewResponse:
    """
    Запустить preview диспетчеризации для списка заказов.
    
    Выполняет симуляцию Gantt-расписания:
    - Расчёт времени начала/окончания задач
    - Учёт времени переналадки между продуктами
    - Выявление конфликтов (пересечения задач на одном рабочем центре)
    
    **Тело запроса:**
    - `manufacturing_order_ids`: Список ID производственных заказов
    - `work_center_id`: ID рабочего центра (опционально, для фильтрации)
    
    **Ответ:**
    - `gantt_preview`: Список задач с временами начала/окончания
    - `conflicts`: Список конфликтов (пересечения задач)
    """
    try:
        preview_result = service.preview_dispatch(
            manufacturing_order_ids=request.manufacturing_order_ids
        )
        
        # Применяем фильтр по work_center_id, если указан
        if request.work_center_id:
            filtered_preview = [
                task for task in preview_result.get("gantt_preview", [])
                if task.get("work_center_id") == str(request.work_center_id)
            ]
            filtered_conflicts = [
                conflict for conflict in preview_result.get("conflicts", [])
                if conflict.get("work_center_id") == str(request.work_center_id)
            ]
            preview_result = {
                "gantt_preview": filtered_preview,
                "conflicts": filtered_conflicts
            }
        
        return DispatchPreviewResponse(
            success=True,
            data=preview_result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка выполнения preview диспетчеризации: {str(e)}"
        )


@router.post("/dispatch-task/{task_id}")
async def dispatch_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    service: DSIZDispatchingService = Depends(get_dsiz_dispatching_service)
):
    """
    Диспетчеризовать задачу на рабочий центр.
    
    Использует DSIZ-специфичную логику:
    - Проверка product_work_center_routing
    - Учёт changeover time
    - Проверка доступности персонала
    
    **Параметры пути:**
    - `task_id`: ID задачи для диспетчеризации
    
    **Тело запроса (опционально):**
    ```json
    {
      "work_center_id": "uuid",
      "scheduled_start": "2026-01-26T08:00:00Z"
    }
    ```
    
    **Ответ:**
    - `task`: Обновлённые данные задачи
    """
    from backend.core.schemas.dispatching import DispatchTaskRequest
    from datetime import datetime
    
    try:
        # Получаем задачу для определения work_center_id
        from backend.core.models.production_task import ProductionTask
        task = db.get(ProductionTask, task_id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Задача {task_id} не найдена"
            )
        
        if not task.work_center_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Задача {task_id} не назначена на рабочий центр"
            )
        
        # Используем метод базового класса dispatch_task
        dispatched_task = service.dispatch_task(
            task_id=task_id,
            work_center_id=task.work_center_id,
            scheduled_start=None  # Автоматический расчёт времени
        )
        
        return {
            "success": True,
            "data": {
                "task": {
                    "id": dispatched_task.id,
                    "task_name": dispatched_task.route_operation.operation_name if dispatched_task.route_operation else "Задача",
                    "work_center_id": dispatched_task.work_center_id,
                    "status": dispatched_task.status.value,
                    "scheduled_start": dispatched_task.started_at,
                    "scheduled_end": dispatched_task.completed_at
                }
            }
        }
    except HTTPException:
        # Перебрасываем HTTPException как есть
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка диспетчеризации задачи: {str(e)}"
        )


@router.get("/work-center-load/{work_center_id}", response_model=WorkCenterLoadResponse)
async def get_work_center_load(
    work_center_id: UUID,
    shift: Optional[str] = Query(None, description="Смена (day/night или 1/2)"),
    db: Session = Depends(get_db),
    service: DSIZDispatchingService = Depends(get_dsiz_dispatching_service)
) -> WorkCenterLoadResponse:
    """
    Получить загрузку рабочего центра с учётом смены.
    
    Использует базовый метод calculate_work_center_load с дополнительной информацией
    о доступности персонала для смены.
    
    **Параметры пути:**
    - `work_center_id`: ID рабочего центра
    
    **Параметры запроса:**
    - `shift`: Идентификатор смены (опционально: "day", "night", "1", "2")
    
    **Ответ:**
    - `load_percentage`: Процент использования (0-100+)
    - `status`: "Available", "Busy", "Overloaded"
    - `available_workers`: Доступные работники для смены
    """
    from datetime import datetime
    
    try:
        # Используем базовый метод для расчёта загрузки
        load_percentage = service.calculate_work_center_load(
            work_center_id=work_center_id,
            date=datetime.utcnow()
        )
        
        # Определяем статус
        if load_percentage < 70:
            load_status = "Available"
        elif load_percentage < 100:
            load_status = "Busy"
        else:
            load_status = "Overloaded"
        
        # Получаем доступных работников для смены
        available_workers = service._get_available_workers_for_shift(
            work_center_id=work_center_id,
            shift=shift
        )
        
        return WorkCenterLoadResponse(
            success=True,
            data={
                "work_center_id": str(work_center_id),
                "load_percentage": load_percentage,
                "status": load_status,
                "date": datetime.utcnow(),
                "shift": shift,
                "available_workers": available_workers
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка расчёта загрузки рабочего центра: {str(e)}"
        )
