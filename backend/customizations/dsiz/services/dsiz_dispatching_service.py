"""
DSIZ Dispatching Service для Phase 2.

Наследует базовый DispatchingService и добавляет:
- Фильтрацию задач по product_work_center_routing
- Учёт времени переналадки (changeover time)
- Проверку доступности персонала через DSIZWorkforceService
- Сортировку по приоритету, FIFO и минимальному changeover
- Preview диспетчеризации с симуляцией Gantt
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_, desc

from backend.core.services.dispatching_service import DispatchingService
from backend.core.models.production_task import ProductionTask
from backend.core.models.work_center import WorkCenter
from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.product import Product
from backend.core.models.route_operation import RouteOperation
from backend.core.models.manufacturing_route import ManufacturingRoute
from backend.core.models.enums import TaskStatus, OrderPriority, WorkCenterStatus
from backend.customizations.dsiz.services.dsiz_workforce_service import DSIZWorkforceService
from backend.config.factory_config import get_factory_config
import yaml
from pathlib import Path


class DSIZDispatchingService(DispatchingService):
    """
    DSIZ-специфичный сервис диспетчеризации.
    
    Расширяет базовый DispatchingService:
    - Фильтрация по product_work_center_routing
    - Учёт changeover time между продуктами
    - Проверка доступности персонала
    - Приоритетная сортировка (URGENT > HIGH > NORMAL > LOW, затем FIFO)
    """
    
    def __init__(self, db: Session):
        """
        Инициализация DSIZ Dispatching Service.
        
        Args:
            db: Сессия базы данных
        """
        super().__init__(db)
        self.workforce = DSIZWorkforceService(db)
        self.config = get_factory_config()
        self._load_dsiz_config()
    
    def _load_dsiz_config(self) -> None:
        """Загрузка DSIZ конфигурации из YAML (MVP)."""
        config_paths = [
            Path("./config/dsiz_config.yaml"),
            Path("./backend/config/dsiz_config.yaml"),
        ]
        
        self.dsiz_config = {}
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        self.dsiz_config = yaml.safe_load(f) or {}
                    break
                except Exception as e:
                    print(f"⚠️  Ошибка загрузки DSIZ конфига {config_path}: {e}")
        
        # Дефолтные значения для MVP
        if not self.dsiz_config:
            self.dsiz_config = {
                'changeover_matrix': {},
                'product_routing': {},
                'workforce': {}
            }
    
    def _get_product_by_id_or_code(self, product_id_str: str) -> Optional[Product]:
        """
        Получить Product по ID (UUID) или product_code.
        
        Args:
            product_id_str: Строка с UUID или product_code
        
        Returns:
            Product или None если не найден
        """
        try:
            product_uuid = UUID(product_id_str)
            product = self.db.get(Product, product_uuid)
            if product:
                return product
        except (ValueError, AttributeError):
            pass
        
        # Если не UUID, ищем по product_code
        product = (
            self.db.query(Product)
            .filter(Product.product_code == product_id_str)
            .first()
        )
        return product
    
    def _get_changeover_time(
        self, 
        prev_product_sku: Optional[str], 
        next_product_sku: str
    ) -> int:
        """
        Получить время переналадки между продуктами (в минутах).
        
        Args:
            prev_product_sku: SKU предыдущего продукта (None если первая задача)
            next_product_sku: SKU следующего продукта
        
        Returns:
            Время переналадки в минутах (0 если совместимы или первая задача)
        """
        if prev_product_sku is None:
            return 0  # Первая задача - нет переналадки
        
        # Получаем compatibility_group из конфига или БД
        # Для MVP используем конфиг
        changeover_matrix = self.dsiz_config.get('changeover_matrix', {})
        
        # Ищем в матрице по SKU или compatibility_group
        # Упрощённая логика для MVP: ищем прямо по SKU
        key = f"{prev_product_sku}->{next_product_sku}"
        if key in changeover_matrix:
            entry = changeover_matrix[key]
            if isinstance(entry, dict):
                return entry.get('setup_time_minutes', 0)
            return int(entry) if isinstance(entry, (int, float)) else 0
        
        # Если не найдено - проверяем обратный порядок
        reverse_key = f"{next_product_sku}->{prev_product_sku}"
        if reverse_key in changeover_matrix:
            entry = changeover_matrix[reverse_key]
            if isinstance(entry, dict):
                return entry.get('setup_time_minutes', 0)
            return int(entry) if isinstance(entry, (int, float)) else 0
        
        # По умолчанию - минимальная переналадка 15 минут
        return 15
    
    def _is_product_allowed_on_work_center(
        self, 
        product_sku: str, 
        work_center_id: UUID
    ) -> bool:
        """
        Проверить, разрешён ли продукт на рабочем центре.
        
        Args:
            product_sku: SKU продукта
            work_center_id: ID рабочего центра
        
        Returns:
            True если продукт разрешён, False если нет
        """
        # Для MVP используем конфиг product_routing
        product_routing = self.dsiz_config.get('product_routing', {})
        
        if product_sku in product_routing:
            routing = product_routing[product_sku]
            # Проверяем, есть ли этот work_center_id в routing
            # В конфиге могут быть строковые ID типа "WC_TUBE_LINE_1"
            # Для MVP упрощаем: проверяем по имени или ID
            for wc_key, wc_config in routing.items():
                if isinstance(wc_config, dict):
                    is_allowed = wc_config.get('is_allowed', True)
                    # TODO: В Phase 2 добавить проверку по UUID из БД
                    if not is_allowed:
                        return False
        
        # Если не найдено в конфиге - разрешаем (нет ограничений)
        return True
    
    def _get_available_workers_for_shift(
        self, 
        work_center_id: UUID, 
        shift: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Получить доступных работников для рабочего центра на смену.
        
        Args:
            work_center_id: ID рабочего центра
            shift: Идентификатор смены (опционально)
        
        Returns:
            Словарь с количеством работников по ролям {"OPERATOR": 2, "PACKER": 1}
        
        Примечание:
            В MVP используем упрощённую логику - возвращаем дефолтные значения.
            В Phase 2 будет загрузка из БД или API смен.
        """
        # Для MVP: возвращаем дефолтные значения из конфига workforce
        workforce_config = self.dsiz_config.get('workforce', {})
        
        # Получаем имя рабочего центра для поиска в конфиге
        work_center = self.db.get(WorkCenter, work_center_id)
        if not work_center:
            return {}
        
        wc_name = work_center.name
        if wc_name in workforce_config:
            roles = workforce_config[wc_name]
            # Преобразуем конфиг в словарь количества
            result = {}
            for role_name, role_config in roles.items():
                if isinstance(role_config, dict):
                    result[role_name] = role_config.get('required_count', 0)
                else:
                    result[role_name] = int(role_config) if isinstance(role_config, (int, float)) else 0
            return result
        
        # Дефолт: 1 оператор
        return {"OPERATOR": 1}
    
    def get_next_task(
        self, 
        work_center_id: UUID
    ) -> Optional[ProductionTask]:
        """
        Получить следующую задачу для диспетчеризации на рабочий центр.
        
        Логика выбора:
        1. Фильтр QUEUED задач по product_work_center_routing
        2. Проверка changeover time (минимальный приоритет)
        3. Проверка доступности персонала
        4. Сортировка: priority.desc (URGENT>HIGH), created_at.asc (FIFO), min changeover
        
        Args:
            work_center_id: ID рабочего центра
        
        Returns:
            ProductionTask или None если нет доступных задач
        """
        # 1. Получаем QUEUED задачи для этого рабочего центра
        # JOIN через order (product_id в ManufacturingOrder - это String, может быть UUID или product_code)
        tasks_query = (
            select(ProductionTask)
            .join(ManufacturingOrder, ProductionTask.order_id == ManufacturingOrder.id)
            .options(
                joinedload(ProductionTask.manufacturing_order),
                joinedload(ProductionTask.route_operation),
                joinedload(ProductionTask.work_center)
            )
            .where(
                and_(
                    ProductionTask.status == TaskStatus.QUEUED,
                    ProductionTask.work_center_id == work_center_id
                )
            )
        )
        
        result = self.db.execute(tasks_query)
        queued_tasks = list(result.unique().scalars().all())
        
        if not queued_tasks:
            return None
        
        # 2. Фильтрация по product_work_center_routing
        filtered_tasks = []
        for task in queued_tasks:
            if task.manufacturing_order and task.manufacturing_order.product_id:
                # Получаем Product: product_id может быть UUID (строка) или product_code
                product_id_str = str(task.manufacturing_order.product_id)
                product = self._get_product_by_id_or_code(product_id_str)
                
                if product and self._is_product_allowed_on_work_center(
                    product.product_code, 
                    work_center_id
                ):
                    filtered_tasks.append(task)
        
        if not filtered_tasks:
            return None
        
        # 3. Проверка доступности персонала
        available_workers = self._get_available_workers_for_shift(work_center_id)
        workforce_available_tasks = []
        
        for task in filtered_tasks:
            # Получаем имя рабочего центра для проверки
            work_center = self.db.get(WorkCenter, work_center_id)
            if work_center:
                wc_name = work_center.name
                if self.workforce.can_run(wc_name, available_workers):
                    workforce_available_tasks.append(task)
        
        if not workforce_available_tasks:
            return None
        
        # 4. Получаем последнюю задачу на рабочем центре для расчёта changeover
        last_task_query = (
            select(ProductionTask)
            .join(ManufacturingOrder, ProductionTask.order_id == ManufacturingOrder.id)
            .join(Product, ManufacturingOrder.product_id == Product.id)
            .where(
                and_(
                    ProductionTask.work_center_id == work_center_id,
                    ProductionTask.status == TaskStatus.IN_PROGRESS,
                    ProductionTask.started_at.isnot(None)
                )
            )
            .order_by(desc(ProductionTask.started_at))
            .limit(1)
        )
        
        last_task_result = self.db.execute(last_task_query)
        last_task = last_task_result.scalar_one_or_none()
        
        prev_product_sku = None
        if last_task and last_task.manufacturing_order:
            product_id_str = str(last_task.manufacturing_order.product_id)
            product = self._get_product_by_id_or_code(product_id_str)
            if product:
                prev_product_sku = product.product_code
        
        # 5. Сортировка: priority, created_at, changeover
        priority_rank = {
            OrderPriority.URGENT: 4,
            OrderPriority.HIGH: 3,
            OrderPriority.NORMAL: 2,
            OrderPriority.LOW: 1,
            None: 0
        }
        
        tasks_with_scores = []
        for task in workforce_available_tasks:
            # Получаем приоритет из заказа
            priority = None
            if task.manufacturing_order and task.manufacturing_order.priority:
                try:
                    priority = OrderPriority(task.manufacturing_order.priority)
                except (ValueError, AttributeError):
                    priority = None
            
            priority_score = priority_rank.get(priority, 0)
            
            # Получаем product_sku для changeover
            next_product_sku = None
            if task.manufacturing_order:
                product_id_str = str(task.manufacturing_order.product_id)
                product = self._get_product_by_id_or_code(product_id_str)
                if product:
                    next_product_sku = product.product_code
            
            changeover_time = self._get_changeover_time(prev_product_sku, next_product_sku) if next_product_sku else 0
            
            tasks_with_scores.append((
                task,
                priority_score,
                task.created_at or datetime.min,
                changeover_time
            ))
        
        # Сортировка: priority (desc), created_at (asc), changeover (asc)
        tasks_with_scores.sort(
            key=lambda x: (-x[1], x[2], x[3])
        )
        
        # Возвращаем первую задачу
        if tasks_with_scores:
            return tasks_with_scores[0][0]
        
        return None
    
    def preview_dispatch(
        self, 
        manufacturing_order_ids: List[UUID]
    ) -> Dict[str, Any]:
        """
        Preview диспетчеризации для списка заказов.
        
        Симулирует Gantt-расписание:
        - task_start = предыдущая задача.end + changeover
        - duration = setup + process + workforce_norm
        - Выявляет конфликты (пересечения задач на одном рабочем центре)
        
        Args:
            manufacturing_order_ids: Список ID производственных заказов
        
        Returns:
            Словарь с:
            - gantt_preview: список задач с временами начала/окончания
            - conflicts: список конфликтов (пересечения)
        """
        # Получаем все задачи для этих заказов
        tasks_query = (
            select(ProductionTask)
            .join(ManufacturingOrder, ProductionTask.order_id == ManufacturingOrder.id)
            .options(
                joinedload(ProductionTask.manufacturing_order),
                joinedload(ProductionTask.route_operation),
                joinedload(ProductionTask.work_center)
            )
            .where(
                and_(
                    ProductionTask.order_id.in_(manufacturing_order_ids),
                    ProductionTask.status == TaskStatus.QUEUED
                )
            )
        )
        
        result = self.db.execute(tasks_query)
        tasks = list(result.unique().scalars().all())
        
        if not tasks:
            return {
                "gantt_preview": [],
                "conflicts": []
            }
        
        # Группируем задачи по рабочим центрам
        tasks_by_wc: Dict[UUID, List[ProductionTask]] = {}
        for task in tasks:
            wc_id = task.work_center_id
            if wc_id not in tasks_by_wc:
                tasks_by_wc[wc_id] = []
            tasks_by_wc[wc_id].append(task)
        
        # Симулируем расписание для каждого рабочего центра
        gantt_preview = []
        conflicts = []
        current_time = datetime.utcnow()
        
        for wc_id, wc_tasks in tasks_by_wc.items():
            # Сортируем задачи по приоритету и FIFO
            priority_rank = {
                OrderPriority.URGENT: 4,
                OrderPriority.HIGH: 3,
                OrderPriority.NORMAL: 2,
                OrderPriority.LOW: 1,
                None: 0
            }
            
            tasks_with_priority = []
            for task in wc_tasks:
                priority = None
                if task.manufacturing_order and task.manufacturing_order.priority:
                    try:
                        priority = OrderPriority(task.manufacturing_order.priority)
                    except (ValueError, AttributeError):
                        priority = None
                
                tasks_with_priority.append((
                    task,
                    priority_rank.get(priority, 0),
                    task.created_at or datetime.min
                ))
            
            tasks_with_priority.sort(key=lambda x: (-x[1], x[2]))
            
            # Получаем последнюю активную задачу на рабочем центре
            last_active_task_query = (
                select(ProductionTask)
                .where(
                    and_(
                        ProductionTask.work_center_id == wc_id,
                        ProductionTask.status == TaskStatus.IN_PROGRESS,
                        ProductionTask.completed_at.isnot(None)
                    )
                )
                .order_by(desc(ProductionTask.completed_at))
                .limit(1)
            )
            
            last_active_result = self.db.execute(last_active_task_query)
            last_active_task = last_active_result.scalar_one_or_none()
            
            prev_end_time = current_time
            prev_product_sku = None
            
            if last_active_task and last_active_task.completed_at:
                prev_end_time = last_active_task.completed_at
                if last_active_task.manufacturing_order:
                    product_id_str = str(last_active_task.manufacturing_order.product_id)
                    product = self._get_product_by_id_or_code(product_id_str)
                    if product:
                        prev_product_sku = product.product_code
            
            # Планируем каждую задачу
            for task, _, _ in tasks_with_priority:
                # Получаем product_sku для changeover
                next_product_sku = None
                if task.manufacturing_order:
                    product_id_str = str(task.manufacturing_order.product_id)
                    product = self._get_product_by_id_or_code(product_id_str)
                    if product:
                        next_product_sku = product.product_code
                
                # Расчёт changeover time
                changeover_minutes = self._get_changeover_time(prev_product_sku, next_product_sku) if next_product_sku else 0
                changeover_delta = timedelta(minutes=changeover_minutes)
                
                # Расчёт длительности задачи
                # duration = setup + process + workforce_norm
                setup_time = timedelta(minutes=changeover_minutes)
                
                # Process time из route_operation
                process_time = timedelta(hours=8)  # Дефолт
                if task.route_operation and task.route_operation.estimated_duration_minutes:
                    process_time = timedelta(minutes=task.route_operation.estimated_duration_minutes)
                
                # Workforce norm (упрощённо - не учитываем деградацию в preview)
                # В реальности нужно учитывать get_effective_rate
                duration = setup_time + process_time
                
                # Время начала = конец предыдущей задачи + changeover
                task_start = prev_end_time + changeover_delta
                task_end = task_start + duration
                
                # Проверка конфликтов (пересечения с другими задачами)
                # Упрощённо: проверяем пересечения только в рамках этого preview
                for existing_task in gantt_preview:
                    if (
                        existing_task['work_center_id'] == str(wc_id) and
                        existing_task['task_start'] < task_end and
                        existing_task['task_end'] > task_start
                    ):
                        conflicts.append({
                            "task_id": str(task.id),
                            "conflict_with": existing_task['task_id'],
                            "work_center_id": str(wc_id),
                            "overlap_start": max(existing_task['task_start'], task_start),
                            "overlap_end": min(existing_task['task_end'], task_end)
                        })
                
                gantt_preview.append({
                    "task_id": str(task.id),
                    "order_id": str(task.order_id),
                    "work_center_id": str(wc_id),
                    "work_center_name": task.work_center.name if task.work_center else "Unknown",
                    "task_start": task_start,
                    "task_end": task_end,
                    "duration_hours": duration.total_seconds() / 3600,
                    "changeover_minutes": changeover_minutes,
                    "status": task.status.value,
                    "priority": task.manufacturing_order.priority if task.manufacturing_order else "NORMAL"
                })
                
                prev_end_time = task_end
                prev_product_sku = next_product_sku
        
        return {
            "gantt_preview": gantt_preview,
            "conflicts": conflicts
        }
