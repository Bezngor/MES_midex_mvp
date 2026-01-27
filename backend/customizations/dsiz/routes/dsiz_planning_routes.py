"""
DSIZ Planning API Routes.

Эндпоинты для запуска DSIZ планирования производства.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, timedelta
from uuid import uuid4

from backend.src.db.session import get_db
from backend.customizations.dsiz.services.dsiz_mrp_service import DSIZMRPService
from backend.customizations.dsiz.schemas.planning import (
    DsizPlanningRequest,
    DsizPlanningResponse,
    PlanningOperation,
    PlanningWarning
)
from backend.core.models.product import Product
from backend.core.models.enums import ProductType

router = APIRouter(prefix="/dsiz", tags=["DSIZ"])


def get_dsiz_mrp_service(db: Session = Depends(get_db)) -> DSIZMRPService:
    """
    Dependency для получения DSIZMRPService.
    
    Args:
        db: Сессия базы данных
    
    Returns:
        DSIZMRPService экземпляр
    """
    return DSIZMRPService(db)


@router.post("/planning/run", response_model=DsizPlanningResponse)
async def run_dsiz_planning(
    request: DsizPlanningRequest,
    db: Session = Depends(get_db),
    mrp: DSIZMRPService = Depends(get_dsiz_mrp_service)
) -> DsizPlanningResponse:
    """
    Запуск DSIZ планирования производства.
    
    Выполняет:
    1. Расчёт нетто-потребности для всех ГП продуктов
    2. Планирование варок реактора по сменам
    3. Учёт ручных блокировок и состояния персонала
    
    **Тело запроса:**
    - `planning_date`: Дата начала планирования
    - `horizon_days`: Горизонт планирования в днях (по умолчанию: 7)
    - `manual_blocks`: Список ручных блокировок (опционально)
    - `workforce_state`: Состояние персонала по сменам (опционально)
    
    **Ответ:**
    - `plan_id`: ID плана планирования
    - `operations`: Список операций планирования (варки реактора)
    - `warnings`: Список предупреждений
    - `summary`: Сводка планирования
    """
    try:
        # Генерируем ID плана
        plan_id = f"DSIZ-PLAN-{request.planning_date.strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"
        
        # 1. Получаем все ГП продукты
        fg_products = db.query(Product).filter(
            Product.product_type == ProductType.FINISHED_GOOD.value
        ).all()
        
        if not fg_products:
            return DsizPlanningResponse(
                success=True,
                plan_id=plan_id,
                planning_date=request.planning_date,
                horizon_days=request.horizon_days,
                operations=[],
                warnings=[
                    PlanningWarning(
                        level="WARNING",
                        message="Не найдено готовых продуктов для планирования"
                    )
                ],
                summary={
                    "total_fg_products": 0,
                    "total_operations": 0,
                    "total_warnings": 1
                }
            )
        
        # 2. Рассчитываем нетто-потребность для каждого ГП
        net_requirements = {}
        warnings = []
        
        for fg_product in fg_products:
            try:
                net_req = mrp.calculate_net_requirement(
                    fg_sku=fg_product.product_code,
                    horizon_days=request.horizon_days
                )
                
                if net_req.net_requirement_kg > 0 and net_req.bulk_product_sku:
                    # Добавляем в словарь потребностей по Bulk продуктам
                    if net_req.bulk_product_sku not in net_requirements:
                        net_requirements[net_req.bulk_product_sku] = 0.0
                    net_requirements[net_req.bulk_product_sku] += net_req.net_requirement_kg
            except ValueError as e:
                warnings.append(PlanningWarning(
                    level="WARNING",
                    message=f"Ошибка расчёта нетто-потребности для {fg_product.product_code}: {str(e)}",
                    context={"fg_sku": fg_product.product_code}
                ))
        
        # 3. Планируем варки реактора по сменам
        operations = []
        current_date = request.planning_date
        
        # Планируем на horizon_days дней
        for day_offset in range(request.horizon_days):
            shift_date = current_date + timedelta(days=day_offset)
            
            # Планируем для каждой смены (1 и 2)
            for shift_num in [1, 2]:
                # Проверяем ручные блокировки
                is_blocked = any(
                    block.work_center_id == "WC_REACTOR_MAIN" and
                    block.shift_date == shift_date and
                    block.shift_num == shift_num
                    for block in request.manual_blocks
                )
                
                if is_blocked:
                    warnings.append(PlanningWarning(
                        level="WARNING",
                        message=f"Смена {shift_num} на {shift_date} заблокирована вручную",
                        context={"shift_date": str(shift_date), "shift_num": shift_num}
                    ))
                    continue
                
                # Планируем варки для этой смены
                if net_requirements:
                    batches = mrp.plan_reactor_batches(
                        mass_demand=net_requirements.copy(),
                        shift_date=shift_date,
                        shift_num=shift_num
                    )
                    
                    for batch in batches:
                        operations.append(PlanningOperation(
                            bulk_product_sku=batch.bulk_product_sku,
                            quantity_kg=batch.quantity_kg,
                            mode=batch.mode,
                            shift_date=batch.shift_date,
                            shift_num=batch.shift_num,
                            reactor_slot=batch.reactor_slot
                        ))
        
        # 4. Формируем сводку
        summary = {
            "total_fg_products": len(fg_products),
            "total_operations": len(operations),
            "total_warnings": len(warnings),
            "net_requirements_kg": sum(net_requirements.values()) if net_requirements else 0.0,
            "planned_shifts": len(set((op.shift_date, op.shift_num) for op in operations))
        }
        
        return DsizPlanningResponse(
            success=True,
            plan_id=plan_id,
            planning_date=request.planning_date,
            horizon_days=request.horizon_days,
            operations=operations,
            warnings=warnings,
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка выполнения DSIZ планирования: {str(e)}"
        )
