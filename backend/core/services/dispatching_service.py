"""
Сервис диспетчеризации и планирования производства.

Обрабатывает:
- Выпуск заказов в производство (PLANNED → RELEASED)
- Создание задач из производственных заказов
- Назначение задач на рабочие центры
- Планирование задач (расчёт времени начала/окончания)
- Управление мощностями
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_, or_

from backend.core.models.production_task import ProductionTask
from backend.core.models.work_center import WorkCenter
from backend.core.models.route_operation import RouteOperation
from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.manufacturing_route import ManufacturingRoute
from backend.core.models.work_center_capacity import WorkCenterCapacity
from backend.core.models.product import Product
from backend.core.models.product_routing_rule import ProductRoutingRule
from backend.core.models.enums import TaskStatus, WorkCenterStatus, OrderStatus, OrderPriority


class DispatchingService:
    """Сервис диспетчеризации и планирования."""

    def __init__(self, db: Session):
        """
        Инициализация сервиса диспетчеризации.

        Args:
            db: Сессия базы данных
        """
        self.db = db

    def dispatch_tasks(self, limit: int = 50) -> list[ProductionTask]:
        """
        Preview dispatching plan: find QUEUED tasks and suggest which work centers
        can execute them (based on route operations and work center availability).

        This is a preview method that does NOT change task statuses.
        Tasks will be started manually via TaskService.start_task.

        Args:
            limit: Maximum number of tasks to consider (default: 50)

        Returns:
            List of ProductionTask objects that can be dispatched,
            sorted by created_at (FIFO), excluding tasks assigned to
            work centers with status DOWN or MAINTENANCE.
        """
        # Find all QUEUED tasks, ordered by created_at (FIFO)
        tasks_query = (
            select(ProductionTask)
            .where(ProductionTask.status == TaskStatus.QUEUED)
            .order_by(ProductionTask.created_at.asc())
            .limit(limit)
        )

        tasks_result = self.db.execute(tasks_query)
        queued_tasks = list(tasks_result.scalars().all())

        if not queued_tasks:
            return []

        # Filter tasks: exclude those assigned to unavailable work centers
        dispatchable_tasks = []
        unavailable_statuses = {WorkCenterStatus.DOWN, WorkCenterStatus.MAINTENANCE}

        for task in queued_tasks:
            # Get work center for this task
            work_center = self.db.get(WorkCenter, task.work_center_id)

            if not work_center:
                # Work center not found - skip this task
                continue

            # Check if work center is available (not DOWN or MAINTENANCE)
            if work_center.status not in unavailable_statuses:
                dispatchable_tasks.append(task)

        return dispatchable_tasks

    def get_dispatch_preview_by_work_center(
        self, limit: int = 50
    ) -> dict[str, list[ProductionTask]]:
        """
        Get dispatch preview grouped by work center.

        Args:
            limit: Maximum number of tasks to consider (default: 50)

        Returns:
            Dictionary mapping work center ID to list of dispatchable tasks
        """
        dispatchable_tasks = self.dispatch_tasks(limit=limit)

        # Group by work center
        by_work_center: dict[str, list[ProductionTask]] = {}
        for task in dispatchable_tasks:
            wc_id_str = str(task.work_center_id)
            if wc_id_str not in by_work_center:
                by_work_center[wc_id_str] = []
            by_work_center[wc_id_str].append(task)

        return by_work_center

    def _get_chosen_work_center_by_rules(self, order: ManufacturingOrder) -> Optional[UUID]:
        """
        По правилам product_routing_rules (приоритет, min/max количество) возвращает РЦ,
        на который нужно направить заказ. Если ни одно правило не подошло — None.
        """
        try:
            product = self.db.get(Product, UUID(str(order.product_id)))
        except (ValueError, TypeError):
            return None
        if not product or not getattr(product, "product_code", None):
            return None
        product_code = (product.product_code or "").strip()
        order_qty = float(order.quantity) if order.quantity is not None else 0
        rules_query = (
            select(ProductRoutingRule)
            .where(ProductRoutingRule.product_code == product_code)
            .order_by(ProductRoutingRule.priority_order.asc())
        )
        rules_list = self.db.execute(rules_query).scalars().all()
        for rule in rules_list:
            if rule.min_quantity is not None and order_qty < rule.min_quantity:
                continue
            if rule.max_quantity is not None and order_qty > rule.max_quantity:
                continue
            return rule.work_center_id
        return None

    def _get_ruled_work_center_ids(self, product_code: str) -> set:
        """Множество work_center_id из правил выбора РЦ для данного продукта (подставляемые РЦ)."""
        rules_query = (
            select(ProductRoutingRule.work_center_id)
            .where(ProductRoutingRule.product_code == product_code)
        )
        return {row[0] for row in self.db.execute(rules_query).fetchall()}

    def release_order(
        self,
        order_id: UUID,
        release_date: Optional[datetime] = None
    ) -> ManufacturingOrder:
        """
        Выпустить заказ в производство (PLANNED/SHIP/IN_WORK → RELEASED).

        Создаёт записи ProductionTask для каждой операции в маршруте.

        Args:
            order_id: ID производственного заказа
            release_date: Дата выпуска (по умолчанию: сейчас)

        Returns:
            Обновлённый ManufacturingOrder

        Raises:
            ValueError: Если заказ не найден или уже выпущен

        Бизнес-правила:
            - Заказ должен быть в статусе PLANNED, SHIP или IN_WORK (заказы из 1С)
            - Один маршрут на продукт (типовой вариант). Правила product_routing_rules задают,
              на какой РЦ направить заказ (по приоритету и min/max количество); операции маршрута
              на «подставляемых» РЦ получают выбранный по правилам РЦ при создании задач.
            - Создаёт задачи на основе маршрута
            - Задачи наследуют приоритет от заказа, начинаются в статусе QUEUED
            - Статус заказа меняется на RELEASED
        """
        order = self.db.get(ManufacturingOrder, order_id)

        if not order:
            raise ValueError(f"Заказ {order_id} не найден")

        releasable = (OrderStatus.PLANNED, OrderStatus.SHIP, OrderStatus.IN_WORK)
        if order.status not in releasable:
            raise ValueError(
                f"Заказ {order.order_number} не в статусе PLANNED/SHIP/IN_WORK (текущий: {order.status})"
            )

        release_date = release_date or datetime.utcnow()

        # Проверяем, есть ли уже задачи для этого заказа
        existing_tasks = (
            self.db.query(ProductionTask)
            .filter(ProductionTask.order_id == order.id)
            .all()
        )

        # Если задач нет, создаём их на основе маршрута
        # Для MVP: если задачи уже есть, просто меняем статус заказа
        if not existing_tasks:
            # Все маршруты для продукта
            routes_query = (
                select(ManufacturingRoute)
                .where(ManufacturingRoute.product_id == order.product_id)
                .order_by(ManufacturingRoute.id)
            )
            routes_result = self.db.execute(routes_query)
            routes_list = routes_result.scalars().all()

            if not routes_list:
                raise ValueError(
                    f"Маршрут производства не найден для продукта {order.product_id}. "
                    f"Создайте маршрут перед выпуском заказа в производство."
                )

            # Один маршрут на продукт (типовой вариант). Правила выбора РЦ задают, на какой РЦ направить заказ.
            route = routes_list[0]
            product = self.db.get(Product, UUID(str(order.product_id)))
            product_code = (product.product_code or "").strip()
            chosen_wc_id = self._get_chosen_work_center_by_rules(order)
            ruled_wc_ids = self._get_ruled_work_center_ids(product_code)

            operations_query = (
                select(RouteOperation)
                .where(RouteOperation.route_id == route.id)
                .order_by(RouteOperation.operation_sequence)
            )
            operations = self.db.execute(operations_query).scalars().all()

            if not operations:
                raise ValueError(
                    f"Маршрут '{route.route_name}' не содержит операций"
                )

            for operation in operations:
                # Если операция на РЦ из правил — подставляем выбранный по правилам РЦ; иначе — РЦ из маршрута
                wc_id = (
                    chosen_wc_id
                    if (chosen_wc_id and operation.work_center_id in ruled_wc_ids)
                    else operation.work_center_id
                )
                task = ProductionTask(
                    order_id=order.id,
                    operation_id=operation.id,
                    work_center_id=wc_id,
                    status=TaskStatus.QUEUED,
                )
                self.db.add(task)

        # Обновляем статус заказа
        order.status = OrderStatus.RELEASED
        order.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(order)

        return order

    def cancel_release(self, order_id: UUID) -> ManufacturingOrder:
        """
        Отменить выпуск заказа (RELEASED → SHIP). Все задачи заказа переводится в CANCELLED.

        Args:
            order_id: ID производственного заказа

        Returns:
            Обновлённый ManufacturingOrder

        Raises:
            ValueError: Если заказ не найден или не в статусе RELEASED
        """
        order = self.db.get(ManufacturingOrder, order_id)
        if not order:
            raise ValueError(f"Заказ {order_id} не найден")
        if order.status != OrderStatus.RELEASED:
            raise ValueError(
                f"Отменить выпуск можно только для заказа в статусе RELEASED (текущий: {order.status})"
            )

        for task in order.production_tasks:
            task.status = TaskStatus.CANCELLED

        order.status = OrderStatus.SHIP
        order.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(order)
        return order

    def dispatch_task(
        self,
        task_id: UUID,
        work_center_id: UUID,
        scheduled_start: Optional[datetime] = None
    ) -> ProductionTask:
        """
        Диспетчеризовать задачу на рабочий центр.

        Args:
            task_id: ID задачи
            work_center_id: ID рабочего центра
            scheduled_start: Запланированное время начала (по умолчанию: сейчас)

        Returns:
            Обновлённая ProductionTask

        Raises:
            ValueError: Если задача/рабочий центр не найден или превышена мощность

        Бизнес-правила:
            - Задача должна быть в статусе QUEUED
            - Рабочий центр должен иметь свободную мощность
            - Статус задачи меняется на IN_PROGRESS (для MVP)
            - Рассчитываются scheduled_start/end времена
        """
        task = self.db.get(ProductionTask, task_id)

        if not task:
            raise ValueError(f"Задача {task_id} не найдена")

        if task.status != TaskStatus.QUEUED:
            raise ValueError(
                f"Задача {task_id} не в статусе QUEUED (текущий: {task.status})"
            )

        work_center = self.db.get(WorkCenter, work_center_id)

        if not work_center:
            raise ValueError(f"Рабочий центр {work_center_id} не найден")

        # Проверка мощности (упрощённая для MVP)
        current_load = self.calculate_work_center_load(work_center_id)
        if current_load >= 100:
            raise ValueError(
                f"Рабочий центр {work_center.name} загружен на {current_load}%"
            )

        scheduled_start = scheduled_start or datetime.utcnow()

        # Рассчитываем длительность (упрощённо: используем фиксированную 8-часовую смену для MVP)
        # TODO: Использовать WorkCenterCapacity и фактические времена обработки
        duration_hours = 8  # Смена по умолчанию
        scheduled_end = scheduled_start + timedelta(hours=duration_hours)

        # Назначаем задачу
        task.work_center_id = work_center_id
        task.status = TaskStatus.IN_PROGRESS  # Для MVP используем IN_PROGRESS вместо DISPATCHED
        # Используем started_at и completed_at для планирования (временно)
        # TODO: Добавить отдельные поля scheduled_start и scheduled_end
        task.started_at = scheduled_start
        task.completed_at = scheduled_end
        task.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(task)

        return task

    def schedule_tasks(
        self,
        work_center_id: Optional[UUID] = None,
        horizon_days: int = 7
    ) -> List[Dict]:
        """
        Запланировать задачи для рабочего центра(ов) в пределах горизонта.

        Генерирует расписание с временами начала/окончания, учитывая:
        - Приоритет (URGENT → HIGH → NORMAL → LOW)
        - Ограничения мощности
        - Отсутствие пересечений на одном рабочем центре

        Args:
            work_center_id: Конкретный рабочий центр (None = все)
            horizon_days: Горизонт планирования в днях

        Returns:
            Список запланированных задач в формате:
            [
                {
                    "task_id": UUID,
                    "task_name": str,
                    "work_center_id": UUID,
                    "work_center_name": str,
                    "priority": str,
                    "scheduled_start": datetime,
                    "scheduled_end": datetime,
                    "duration_hours": float,
                    "status": str
                },
                ...
            ]

        Бизнес-правила:
            - Задачи сортируются по приоритету, затем по due_date
            - Включаются задачи со статусами IN_PROGRESS и QUEUED (если назначены)
            - Задачи планируются последовательно (без пересечений)
            - Учитывается доступность рабочего центра (8 часов/день для MVP)
        """
        # Строим запрос с eager loading для избежания N+1 проблем
        query = (
            self.db.query(ProductionTask)
            .options(
                joinedload(ProductionTask.manufacturing_order),
                joinedload(ProductionTask.route_operation),
                joinedload(ProductionTask.work_center)
            )
            .filter(
                or_(
                    ProductionTask.status == TaskStatus.IN_PROGRESS,
                    ProductionTask.status == TaskStatus.QUEUED
                )
            )
        )

        if work_center_id:
            query = query.filter(ProductionTask.work_center_id == work_center_id)

        tasks = query.all()

        # Сортируем по приоритету (URGENT первым), затем по scheduled_start
        priority_rank = {
            OrderPriority.URGENT: 4,
            OrderPriority.HIGH: 3,
            OrderPriority.NORMAL: 2,
            OrderPriority.LOW: 1,
            None: 0
        }

        # Получаем приоритет из заказа
        # Используем уже загруженный manufacturing_order через relationship
        tasks_with_priority = []
        for task in tasks:
            priority = None
            # Используем relationship вместо отдельного запроса
            if task.manufacturing_order and task.manufacturing_order.priority:
                try:
                    priority = OrderPriority(task.manufacturing_order.priority)
                except (ValueError, AttributeError):
                    priority = None
            tasks_with_priority.append((task, priority))

        # Сортируем задачи: сначала по приоритету (высший первым), затем по времени начала
        # Для задач без started_at используем datetime.max для сортировки в конец
        from datetime import timezone
        max_datetime = datetime.max.replace(tzinfo=timezone.utc)
        
        tasks_sorted = sorted(
            tasks_with_priority,
            key=lambda t: (
                -priority_rank.get(t[1], 0),
                t[0].started_at if t[0].started_at else max_datetime
            )
        )

        # Строим расписание
        schedule = []
        for task, priority in tasks_sorted:
            # Рассчитываем длительность
            if task.started_at and task.completed_at:
                duration = (task.completed_at - task.started_at).total_seconds() / 3600
            else:
                duration = 8  # По умолчанию

            # Получаем имя задачи из операции маршрута
            task_name = "Задача без операции"
            if task.route_operation:
                task_name = task.route_operation.operation_name
            elif task.manufacturing_order:
                task_name = f"Производство {task.manufacturing_order.order_number}"

            # Безопасное получение work_center_id и имени
            work_center_id_val = task.work_center_id
            work_center_name = "Не назначен"
            if task.work_center:
                work_center_name = task.work_center.name
            elif work_center_id_val:
                # Если work_center не загружен, но ID есть, пытаемся загрузить
                work_center = self.db.get(WorkCenter, work_center_id_val)
                if work_center:
                    work_center_name = work_center.name

            schedule.append({
                "task_id": task.id,
                "task_name": task_name,
                "work_center_id": work_center_id_val,
                "work_center_name": work_center_name,
                "priority": priority.value if priority else "NORMAL",
                "scheduled_start": task.started_at,
                "scheduled_end": task.completed_at,
                "duration_hours": round(duration, 2),
                "status": task.status.value
            })

        return schedule

    def calculate_work_center_load(
        self,
        work_center_id: UUID,
        date: Optional[datetime] = None
    ) -> float:
        """
        Рассчитать загрузку рабочего центра (процент использования).

        Args:
            work_center_id: ID рабочего центра
            date: Дата для расчёта (по умолчанию: сегодня)

        Returns:
            Процент использования (0-100+)

        Бизнес-правила:
            - Загрузка = (сумма часов активных задач / доступные часы мощности) * 100
            - Активные задачи: только IN_PROGRESS (диспетчеризованные задачи)
            - QUEUED задачи НЕ учитываются (они еще не запланированы)
            - Используется estimated_duration_minutes из RouteOperation
            - Учитывается parallel_capacity рабочего центра
            - Доступная мощность: 8 часов/смена (MVP)
            - Может превышать 100% (указывает на перегрузку)
        """
        date = date or datetime.utcnow()

        # Получаем рабочий центр
        work_center = self.db.get(WorkCenter, work_center_id)
        if not work_center:
            return 0.0

        # Получаем активные задачи для рабочего центра на дату
        # Учитываем ТОЛЬКО задачи со статусом IN_PROGRESS (диспетчеризованные)
        # QUEUED задачи не учитываются, так как они еще не запланированы
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        # Получаем только диспетчеризованные задачи (IN_PROGRESS)
        # Важно: QUEUED задачи НЕ учитываются, так как они еще не запланированы
        # Загружаем связанные данные (route_operation) для получения estimated_duration_minutes
        tasks = (
            self.db.query(ProductionTask)
            .options(joinedload(ProductionTask.route_operation))
            .filter(
                ProductionTask.work_center_id == work_center_id,
                ProductionTask.status == TaskStatus.IN_PROGRESS,
                ProductionTask.started_at.isnot(None),  # Только задачи с запланированным временем
                ProductionTask.started_at >= start_of_day,
                ProductionTask.started_at < end_of_day
            )
            .all()
        )

        # Рассчитываем общее количество часов для всех задач
        total_hours = 0
        for task in tasks:
            if task.started_at and task.completed_at:
                # Используем запланированное время, если оно есть
                duration = (task.completed_at - task.started_at).total_seconds() / 3600
                total_hours += duration
            elif task.route_operation and task.route_operation.estimated_duration_minutes:
                # Используем estimated_duration из операции маршрута
                duration_minutes = task.route_operation.estimated_duration_minutes
                duration = duration_minutes / 60.0
                total_hours += duration
            else:
                # Fallback: используем значение по умолчанию только если нет других данных
                # Но это не должно происходить для диспетчеризованных задач
                total_hours += 8

        # Доступная мощность с учетом parallel_capacity
        # Если parallel_capacity = 2, то можно обрабатывать 2 задачи параллельно
        # Доступные часы = 8 часов * parallel_capacity
        parallel_capacity = work_center.parallel_capacity if work_center.parallel_capacity else 1
        available_hours = 8 * parallel_capacity  # 8 часов/смена * количество параллельных задач

        # Рассчитываем использование
        utilization = (total_hours / available_hours) * 100 if available_hours > 0 else 0

        return round(utilization, 2)

    def get_gantt_data(
        self,
        work_center_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Получить данные для диаграммы Ганта для визуализации.

        Args:
            work_center_id: Фильтр по рабочему центру (None = все)
            start_date: Дата начала (по умолчанию: сегодня)
            end_date: Дата окончания (по умолчанию: +7 дней)

        Returns:
            Структура данных Ганта:
            {
                "work_centers": [
                    {
                        "id": UUID,
                        "name": str,
                        "tasks": [
                            {
                                "id": UUID,
                                "name": str,
                                "start": datetime,
                                "end": datetime,
                                "priority": str,
                                "status": str,
                                "order_number": str
                            },
                            ...
                        ]
                    },
                    ...
                ],
                "start_date": datetime,
                "end_date": datetime
            }
        """
        start_date = start_date or datetime.utcnow()
        end_date = end_date or start_date + timedelta(days=7)

        # Получаем рабочие центры
        wc_query = self.db.query(WorkCenter)
        if work_center_id:
            wc_query = wc_query.filter(WorkCenter.id == work_center_id)

        work_centers = wc_query.all()

        gantt_data = {
            "work_centers": [],
            "start_date": start_date,
            "end_date": end_date
        }

        for wc in work_centers:
            # Задачи: IN_PROGRESS или QUEUED в диапазоне дат.
            # Для QUEUED без started_at считаем по created_at (попадание в диапазон).
            tasks_started = (
                self.db.query(ProductionTask)
                .filter(
                    ProductionTask.work_center_id == wc.id,
                    ProductionTask.started_at >= start_date,
                    ProductionTask.started_at <= end_date,
                    or_(
                        ProductionTask.status == TaskStatus.IN_PROGRESS,
                        ProductionTask.status == TaskStatus.QUEUED,
                    ),
                )
                .order_by(ProductionTask.started_at)
                .all()
            )
            tasks_queued_no_start = (
                self.db.query(ProductionTask)
                .filter(
                    ProductionTask.work_center_id == wc.id,
                    ProductionTask.status == TaskStatus.QUEUED,
                    ProductionTask.started_at.is_(None),
                    ProductionTask.created_at >= start_date,
                    ProductionTask.created_at <= end_date,
                )
                .order_by(ProductionTask.created_at)
                .all()
            )
            # Объединяем без дубликатов (QUEUED с started_at уже в tasks_started)
            seen_ids = {t.id for t in tasks_started}
            tasks = list(tasks_started)
            for t in tasks_queued_no_start:
                if t.id not in seen_ids:
                    seen_ids.add(t.id)
                    tasks.append(t)
            tasks.sort(key=lambda t: (t.started_at or t.created_at) or datetime.min.replace(tzinfo=timezone.utc))

            task_data = []
            for task in tasks:
                task_name = "Задача без операции"
                if task.route_operation:
                    task_name = task.route_operation.operation_name
                elif task.manufacturing_order:
                    task_name = f"Производство {task.manufacturing_order.order_number}"

                product_name = None
                quantity_display = None
                if task.manufacturing_order:
                    try:
                        prod = self.db.get(Product, UUID(task.manufacturing_order.product_id))
                        product_name = (prod.product_name or prod.product_code) if prod else None
                    except (ValueError, TypeError, AttributeError):
                        pass
                    if task.quantity_pcs is not None:
                        quantity_display = f"{int(task.quantity_pcs)} шт"
                    elif task.quantity_kg is not None:
                        quantity_display = f"{float(task.quantity_kg)} кг"
                    elif task.manufacturing_order.quantity is not None:
                        q = float(task.manufacturing_order.quantity)
                        quantity_display = f"{int(q)} шт" if q == int(q) else f"{q} кг"

                priority = "NORMAL"
                if task.manufacturing_order and task.manufacturing_order.priority:
                    priority = task.manufacturing_order.priority

                start = task.started_at or task.created_at
                end = task.completed_at
                if end is None and task.route_operation and start:
                    mins = getattr(task.route_operation, "estimated_duration_minutes", None) or 60
                    end = start + timedelta(minutes=mins)
                elif end is None and start:
                    end = start + timedelta(minutes=60)

                task_data.append({
                    "id": task.id,
                    "name": task_name,
                    "product_name": product_name,
                    "quantity_display": quantity_display,
                    "start": start,
                    "end": end,
                    "priority": priority,
                    "status": task.status.value,
                    "order_number": task.manufacturing_order.order_number if task.manufacturing_order else "N/A"
                })

            gantt_data["work_centers"].append({
                "id": wc.id,
                "name": wc.name,
                "tasks": task_data
            })

        return gantt_data

    def find_available_work_center(
        self,
        product_id: str,  # В текущей модели это String, не UUID
        required_date: datetime
    ) -> Optional[UUID]:
        """
        Найти доступный рабочий центр для продукта.

        Args:
            product_id: Продукт для производства
            required_date: Требуемая дата начала

        Returns:
            ID рабочего центра или None, если нет доступной мощности

        Бизнес-правила:
            - Проверяет WorkCenterCapacity для продукта
            - Рассчитывает текущую загрузку на required_date
            - Возвращает первый рабочий центр с <80% использования
        """
        # Получаем рабочие центры с мощностью для этого продукта
        # Примечание: product_id в WorkCenterCapacity - это UUID, но в ManufacturingOrder - String
        # Для MVP: ищем по product_id как строке (если это UUID в строковом формате)
        try:
            product_uuid = UUID(product_id)
        except ValueError:
            # Если это не UUID, возвращаем None
            return None

        capacities = self.db.query(WorkCenterCapacity).filter(
            WorkCenterCapacity.product_id == product_uuid
        ).all()

        if not capacities:
            return None

        # Находим рабочий центр с наименьшей загрузкой
        best_wc = None
        best_load = 100

        for cap in capacities:
            load = self.calculate_work_center_load(
                cap.work_center_id,
                required_date
            )

            if load < 80 and load < best_load:
                best_wc = cap.work_center_id
                best_load = load

        return best_wc
