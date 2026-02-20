"""
Сервис стратегического планирования производства.

Реализует алгоритм пересчёта плана производства на основе принятых заказов покупателей.
См. STRATEGIC_PLANNING_ALGORITHM.md для детального описания алгоритма.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.bill_of_material import BillOfMaterial
from backend.core.models.inventory_balance import InventoryBalance
from backend.core.models.manufacturing_route import ManufacturingRoute
from backend.core.models.product import Product
from backend.core.models.production_task import ProductionTask
from backend.core.models.route_operation import RouteOperation
from backend.core.models.enums import OrderPriority, ProductStatus, ProductType, TaskStatus
from backend.core.services.mrp_service import MRPService

# Границы смен (часы в UTC): СМЕНА1 08:00–20:00, СМЕНА2 20:00–08:00
SHIFT1_START_HOUR = 8
SHIFT1_END_HOUR = 20
SHIFT_DURATION_HOURS = 12
MINUTES_PER_SHIFT = SHIFT_DURATION_HOURS * 60


class MassRouteValidationError(Exception):
    """Ошибка валидации маршрута массы: отсутствует маршрут или операции."""

    def __init__(self, mass_product_id: UUID, mass_product_name: str, order_id: UUID, order_number: str, reason: str):
        self.mass_product_id = mass_product_id
        self.mass_product_name = mass_product_name
        self.order_id = order_id
        self.order_number = order_number
        self.reason = reason
        super().__init__(f"Для массы {mass_product_name} (ID: {mass_product_id}) в заказе {order_number} (ID: {order_id}): {reason}")


class ComponentReservationResult:
    """Результат резервирования компонентов для заказа."""

    def __init__(
        self,
        order_id: UUID,
        success: bool,
        reserved_components: Optional[Dict[UUID, float]] = None,
        missing_components: Optional[Dict[UUID, float]] = None,
    ):
        self.order_id = order_id
        self.success = success
        self.reserved_components = reserved_components or {}
        self.missing_components = missing_components or {}


class StrategicPlanningService:
    """Сервис стратегического планирования производства."""

    def __init__(self, db: Session):
        self.db = db
        self.mrp_service = MRPService(db)

    def reset_plan_and_reservations(self) -> Dict:
        """
        Сбросить план и резервы к начальному состоянию:
        - обнулить reserved_quantity во всех остатках (inventory_balances);
        - удалить все запланированные задачи со статусом QUEUED (production_tasks).

        Returns:
            {"tasks_deleted": int, "reserves_cleared": int}
        """
        tasks_deleted = (
            self.db.query(ProductionTask).filter(ProductionTask.status == TaskStatus.QUEUED).delete(synchronize_session=False)
        )
        reserves_cleared = 0
        for inv in self.db.query(InventoryBalance).filter(InventoryBalance.reserved_quantity > 0).all():
            inv.reserved_quantity = 0.0
            reserves_cleared += 1
        self.db.commit()
        return {"tasks_deleted": tasks_deleted, "reserves_cleared": reserves_cleared}

    def recalculate_plan(
        self,
        accepted_order_ids: List[UUID],
    ) -> Dict:
        """
        Пересчитать план производства для принятых заказов.

        Args:
            accepted_order_ids: Список ID заказов, отмеченных "Принять"

        Returns:
            Словарь с результатами планирования:
            {
                "success": bool,
                "reserved_orders": List[UUID],  # Заказы с успешно зарезервированными компонентами
                "failed_orders": List[Dict],    # Заказы с ошибками резервирования
                "planned_operations": List[Dict] # Запланированные операции
            }
        """
        # Получаем заказы с их приоритетами
        orders = (
            self.db.query(ManufacturingOrder)
            .filter(ManufacturingOrder.id.in_(accepted_order_ids))
            .all()
        )

        # Перед пересчётом снимаем ранее созданные резервы и запланированные задачи по этим заказам,
        # чтобы повторное нажатие «Пересчитать план» не приводило к дублям резервов и росту числа ошибок.
        self._release_reservations_and_planned_tasks_for_orders(orders)
        self.db.flush()

        # Группируем заказы по приоритетам
        orders_by_priority: Dict[OrderPriority, List[ManufacturingOrder]] = {
            OrderPriority.URGENT: [],
            OrderPriority.HIGH: [],
            OrderPriority.NORMAL: [],
            OrderPriority.LOW: [],
        }

        for order in orders:
            try:
                priority = OrderPriority(order.priority) if order.priority else OrderPriority.NORMAL
            except (ValueError, AttributeError):
                priority = OrderPriority.NORMAL
            orders_by_priority[priority].append(order)

        # Этап 1: Резервирование компонентов BOM (по приоритетам)
        reservation_results: Dict[UUID, ComponentReservationResult] = {}

        for priority in [OrderPriority.URGENT, OrderPriority.HIGH, OrderPriority.NORMAL, OrderPriority.LOW]:
            for order in orders_by_priority[priority]:
                result = self._reserve_components_for_order(order)
                reservation_results[order.id] = result

        # Разделяем на успешные и неуспешные; для неуспешных — детали по компонентам (имя, остаток, потребность, дефицит)
        orders_by_id = {o.id: o for o in orders}
        successful_orders = [
            order_id
            for order_id, result in reservation_results.items()
            if result.success
        ]
        failed_orders = []
        for result in reservation_results.values():
            if result.success:
                continue
            order = orders_by_id.get(result.order_id)
            order_number = order.order_number if order else ""
            order_product_name = ""
            if order:
                try:
                    prod = self.db.get(Product, UUID(order.product_id))
                    order_product_name = (prod.product_name or prod.product_code or str(order.product_id)) if prod else str(order.product_id)
                except (ValueError, TypeError, AttributeError):
                    order_product_name = str(order.product_id)
            missing_details = []
            for comp_id, deficit_qty in result.missing_components.items():
                available = self._get_available_quantity(comp_id)
                required_qty = available + deficit_qty
                comp_product = self.db.get(Product, comp_id)
                comp_name = (comp_product.product_name or comp_product.product_code or str(comp_id)) if comp_product else str(comp_id)
                missing_details.append({
                    "component_id": str(comp_id),
                    "component_name": comp_name,
                    "required_qty": round(required_qty, 4),
                    "available_qty": round(available, 4),
                    "deficit_qty": round(deficit_qty, 4),
                })
            failed_orders.append({
                "order_id": str(result.order_id),
                "order_number": order_number,
                "order_product_name": order_product_name,
                "missing_components": {str(cid): qty for cid, qty in result.missing_components.items()},
                "missing_details": missing_details,
            })

        # Этап 2: Планирование операций производства (по приоритетам)
        planned_operations = []
        mass_validation_errors = []  # Ошибки валидации маршрутов масс
        mass_planning_info = []  # Информация о массах, которые требовались для планирования

        for priority in [OrderPriority.URGENT, OrderPriority.HIGH, OrderPriority.NORMAL, OrderPriority.LOW]:
            priority_orders = [
                order
                for order in orders_by_priority[priority]
                if order.id in successful_orders
            ]
            for order in priority_orders:
                try:
                    operations = self._plan_operations_for_order(order, reservation_results[order.id], mass_planning_info)
                    planned_operations.extend(operations)
                except MassRouteValidationError as e:
                    # Ошибка валидации маршрута массы - блокируем планирование
                    mass_validation_errors.append({
                        "mass_product_id": str(e.mass_product_id),
                        "mass_product_name": e.mass_product_name,
                        "order_id": str(e.order_id),
                        "order_number": e.order_number,
                        "reason": e.reason,
                    })
                    # Удаляем заказ из успешных, чтобы он не попал в reserved_orders
                    if order.id in successful_orders:
                        successful_orders.remove(order.id)
                    # Освобождаем резервы для этого заказа
                    self._release_reservations_for_order(order)

        return {
            "success": True,
            "reserved_orders": [str(oid) for oid in successful_orders],
            "failed_orders": failed_orders,
            "planned_operations": planned_operations,
            "mass_validation_errors": mass_validation_errors,  # Ошибки валидации маршрутов масс
            "mass_planning_info": mass_planning_info,  # Информация о массах для анализа отсутствия задач на Реакторе
        }

    def _reserve_components_for_order(
        self, order: ManufacturingOrder
    ) -> ComponentReservationResult:
        """
        Резервировать компоненты BOM для заказа.

        Алгоритм:
        1. Декомпозировать BOM (уровень ГП и уровень Массы)
        2. Проверить доступность всех компонентов уровня ГП
        3. Если не хватает Массы, проверить уровень Массы
        4. Резервировать все компоненты только если всех хватает
        """
        # product_id в ManufacturingOrder хранится как String
        try:
            product_id = UUID(order.product_id)
        except (ValueError, AttributeError, TypeError):
            return ComponentReservationResult(
                order_id=order.id,
                success=False,
                missing_components={},
            )
        required_quantity = float(order.quantity)

        # Получаем прямые компоненты уровня ГП
        fg_bom_entries = (
            self.db.query(BillOfMaterial)
            .filter(BillOfMaterial.parent_product_id == product_id)
            .all()
        )

        if not fg_bom_entries:
            # Нет BOM - возможно, это сырьё или ошибка
            return ComponentReservationResult(
                order_id=order.id,
                success=False,
                missing_components={product_id: required_quantity},
            )

        # Разделяем компоненты на уровень ГП и Массу (BULK)
        mass_product_id = None
        mass_required_qty = 0.0
        fg_components: Dict[UUID, float] = {}

        for bom_entry in fg_bom_entries:
            child_id = bom_entry.child_product_id
            child_product = self.db.get(Product, child_id)

            # Проверяем, является ли компонент Массой (BULK)
            if child_product and child_product.product_type == ProductType.BULK.value:
                mass_product_id = child_id
                mass_required_qty = float(bom_entry.quantity) * required_quantity
            else:
                # Обычный компонент уровня ГП
                required_qty = float(bom_entry.quantity) * required_quantity
                fg_components[child_id] = required_qty

        # Шаг 1: Проверяем доступность всех компонентов уровня ГП
        missing_fg_components: Dict[UUID, float] = {}
        for comp_id, required_qty in fg_components.items():
            available = self._get_available_quantity(comp_id)
            if available < required_qty:
                missing_fg_components[comp_id] = required_qty - available

        # Шаг 2: Если есть Масса, проверяем её доступность и компоненты Массы
        missing_mass_components: Dict[UUID, float] = {}
        if mass_product_id and mass_required_qty > 0:
            mass_available = self._get_available_quantity(mass_product_id)
            if mass_available < mass_required_qty:
                # Не хватает Массы - проверяем компоненты уровня Массы
                mass_bom_entries = (
                    self.db.query(BillOfMaterial)
                    .filter(BillOfMaterial.parent_product_id == mass_product_id)
                    .all()
                )

                if not mass_bom_entries:
                    # Нет BOM для Массы - это ошибка
                    missing_mass_components[mass_product_id] = mass_required_qty - mass_available
                else:
                    # Проверяем доступность всех компонентов Массы
                    mass_components: Dict[UUID, float] = {}
                    for bom_entry in mass_bom_entries:
                        comp_id = bom_entry.child_product_id
                        required_qty = float(bom_entry.quantity) * mass_required_qty
                        mass_components[comp_id] = required_qty

                    for comp_id, required_qty in mass_components.items():
                        available = self._get_available_quantity(comp_id)
                        if available < required_qty:
                            missing_mass_components[comp_id] = required_qty - available

        # Если есть недостающие компоненты, ничего не резервируем
        all_missing = {**missing_fg_components, **missing_mass_components}
        if all_missing:
            return ComponentReservationResult(
                order_id=order.id,
                success=False,
                missing_components=all_missing,
            )

        # Шаг 3: Резервируем все компоненты (только если всех хватает)
        reserved_components: Dict[UUID, float] = {}

        try:
            # Резервируем компоненты уровня ГП
            for comp_id, required_qty in fg_components.items():
                self._reserve_component(comp_id, required_qty)
                reserved_components[comp_id] = required_qty

            # Если нужна Масса и её нет на остатке, резервируем компоненты Массы
            if mass_product_id and mass_required_qty > 0:
                mass_available = self._get_available_quantity(mass_product_id)
                if mass_available < mass_required_qty:
                    # Резервируем компоненты Массы
                    mass_bom_entries = (
                        self.db.query(BillOfMaterial)
                        .filter(BillOfMaterial.parent_product_id == mass_product_id)
                        .all()
                    )
                    for bom_entry in mass_bom_entries:
                        comp_id = bom_entry.child_product_id
                        required_qty = float(bom_entry.quantity) * mass_required_qty
                        self._reserve_component(comp_id, required_qty)
                        reserved_components[comp_id] = required_qty

            # Коммитим резервирование
            self.db.commit()

            return ComponentReservationResult(
                order_id=order.id,
                success=True,
                reserved_components=reserved_components,
            )
        except Exception as e:
            # Откатываем транзакцию при ошибке
            self.db.rollback()
            return ComponentReservationResult(
                order_id=order.id,
                success=False,
                missing_components={},
            )

    def _get_available_quantity(self, product_id: UUID) -> float:
        """Получить доступное количество продукта (quantity - reserved_quantity)."""
        inventories = (
            self.db.query(InventoryBalance)
            .filter(
                InventoryBalance.product_id == product_id,
                InventoryBalance.product_status == ProductStatus.FINISHED,
            )
            .all()
        )

        total_available = sum(
            float(inv.quantity) - float(inv.reserved_quantity)
            for inv in inventories
        )

        return max(0.0, total_available)

    def _reserve_component(self, product_id: UUID, quantity: float) -> None:
        """
        Зарезервировать компонент в инвентаре.

        Резервирует количество из доступных остатков (FIFO).
        """
        remaining = quantity
        inventories = (
            self.db.query(InventoryBalance)
            .filter(
                InventoryBalance.product_id == product_id,
                InventoryBalance.product_status == ProductStatus.FINISHED,
            )
            .order_by(InventoryBalance.created_at.asc())  # FIFO
            .all()
        )

        for inv in inventories:
            if remaining <= 0:
                break

            available = float(inv.quantity) - float(inv.reserved_quantity)
            if available > 0:
                reserve_amount = min(remaining, available)
                inv.reserved_quantity = float(inv.reserved_quantity) + reserve_amount
                remaining -= reserve_amount

        if remaining > 0:
            raise ValueError(
                f"Недостаточно доступного количества для резервирования продукта {product_id}. "
                f"Требуется: {quantity}, доступно: {quantity - remaining}"
            )

    def _get_required_components_for_order(self, order: ManufacturingOrder) -> Dict[UUID, float]:
        """
        Возвращает словарь (product_id -> количество) компонентов, которые нужны для заказа
        (уровень ГП + при необходимости уровень Массы). Без резервирования.
        """
        try:
            product_id = UUID(order.product_id)
        except (ValueError, AttributeError, TypeError):
            return {}
        required_quantity = float(order.quantity)
        fg_bom_entries = (
            self.db.query(BillOfMaterial)
            .filter(BillOfMaterial.parent_product_id == product_id)
            .all()
        )
        if not fg_bom_entries:
            return {}
        mass_product_id = None
        mass_required_qty = 0.0
        components: Dict[UUID, float] = {}
        for bom_entry in fg_bom_entries:
            child_id = bom_entry.child_product_id
            child_product = self.db.get(Product, child_id)
            if child_product and child_product.product_type == ProductType.BULK.value:
                mass_product_id = child_id
                mass_required_qty = float(bom_entry.quantity) * required_quantity
            else:
                components[child_id] = float(bom_entry.quantity) * required_quantity
        if mass_product_id and mass_required_qty > 0:
            mass_bom_entries = (
                self.db.query(BillOfMaterial)
                .filter(BillOfMaterial.parent_product_id == mass_product_id)
                .all()
            )
            for bom_entry in mass_bom_entries:
                comp_id = bom_entry.child_product_id
                qty = float(bom_entry.quantity) * mass_required_qty
                components[comp_id] = components.get(comp_id, 0.0) + qty
        return components

    def _release_component(self, product_id: UUID, quantity: float) -> None:
        """Снять резерв с компонента (уменьшить reserved_quantity), LIFO по записям остатков."""
        remaining = quantity
        inventories = (
            self.db.query(InventoryBalance)
            .filter(
                InventoryBalance.product_id == product_id,
                InventoryBalance.product_status == ProductStatus.FINISHED,
            )
            .order_by(InventoryBalance.created_at.desc())
            .all()
        )
        for inv in inventories:
            if remaining <= 0:
                break
            reserved = float(inv.reserved_quantity)
            if reserved > 0:
                release_amount = min(remaining, reserved)
                inv.reserved_quantity = max(0.0, reserved - release_amount)
                remaining -= release_amount
        if remaining > 0:
            pass  # Снимаем сколько есть; лишнее могло быть зарезервировано в другой сессии

    def _release_reservations_for_order(self, order: ManufacturingOrder) -> None:
        """Снять резервы по компонентам для одного заказа."""
        required_components = self._get_required_components_for_order(order)
        for comp_id, qty in required_components.items():
            self._release_component(comp_id, qty)

    def _release_reservations_and_planned_tasks_for_orders(
        self, orders: List[ManufacturingOrder]
    ) -> None:
        """Снять резервы по компонентам для переданных заказов и удалить их запланированные задачи (QUEUED)."""
        if not orders:
            return
        order_ids = [o.id for o in orders]
        # Удаляем запланированные задачи (созданные предыдущим пересчётом)
        self.db.query(ProductionTask).filter(
            ProductionTask.order_id.in_(order_ids),
            ProductionTask.status == TaskStatus.QUEUED,
        ).delete(synchronize_session=False)
        # Суммируем требуемые компоненты по всем заказам и снимаем резерв
        total_to_release: Dict[UUID, float] = {}
        for order in orders:
            for comp_id, qty in self._get_required_components_for_order(order).items():
                total_to_release[comp_id] = total_to_release.get(comp_id, 0.0) + qty
        for comp_id, qty in total_to_release.items():
            self._release_component(comp_id, qty)

    def _get_route_and_operations(self, product_id_str: str) -> Optional[Tuple[ManufacturingRoute, List[RouteOperation]]]:
        """Получить маршрут и операции для продукта по product_id (строка)."""
        route_result = self.db.execute(
            select(ManufacturingRoute).where(ManufacturingRoute.product_id == product_id_str)
        )
        route = route_result.scalar_one_or_none()
        if not route:
            return None
        ops_result = self.db.execute(
            select(RouteOperation)
            .where(RouteOperation.route_id == route.id)
            .order_by(RouteOperation.operation_sequence)
        )
        operations = list(ops_result.scalars().all())
        if not operations:
            return None
        return (route, operations)

    def _get_busy_intervals(self, work_center_id: UUID) -> List[Tuple[datetime, datetime]]:
        """Получить занятые интервалы на РЦ по задачам со статусом QUEUED/IN_PROGRESS и заданным временем."""
        tasks = (
            self.db.query(ProductionTask)
            .filter(
                ProductionTask.work_center_id == work_center_id,
                ProductionTask.status.in_([TaskStatus.QUEUED, TaskStatus.IN_PROGRESS]),
                ProductionTask.started_at.isnot(None),
                ProductionTask.completed_at.isnot(None),
            )
            .order_by(ProductionTask.started_at)
            .all()
        )
        return [(t.started_at, t.completed_at) for t in tasks if t.started_at and t.completed_at]

    def _align_to_shift_start(self, dt: datetime) -> datetime:
        """Привести время к началу ближайшей смены (08:00 или 20:00 в тот же день)."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        day = dt.date()
        shift1_start = datetime(day.year, day.month, day.day, SHIFT1_START_HOUR, 0, 0, tzinfo=timezone.utc)
        shift2_start = datetime(day.year, day.month, day.day, SHIFT1_END_HOUR, 0, 0, tzinfo=timezone.utc)
        if dt < shift1_start:
            return shift1_start
        if dt < shift2_start:
            return shift1_start if dt.hour < SHIFT1_START_HOUR else shift2_start
        next_day = day + timedelta(days=1)
        return datetime(next_day.year, next_day.month, next_day.day, SHIFT1_START_HOUR, 0, 0, tzinfo=timezone.utc)

    def _get_shift_boundaries(self, dt: datetime) -> Tuple[datetime, datetime]:
        """Для заданного момента вернуть (начало смены, конец смены) той смены, в которую попадает dt."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        day = dt.date()
        shift1_start = datetime(day.year, day.month, day.day, SHIFT1_START_HOUR, 0, 0, tzinfo=timezone.utc)
        shift1_end = shift1_start + timedelta(hours=SHIFT_DURATION_HOURS)
        shift2_start = shift1_end
        shift2_end = shift2_start + timedelta(hours=SHIFT_DURATION_HOURS)
        if dt < shift1_end:
            return (shift1_start, shift1_end)
        return (shift2_start, shift2_end)

    def _find_next_free_slot(
        self,
        work_center_id: UUID,
        duration_minutes: int,
        from_dt: datetime,
    ) -> Optional[Tuple[datetime, datetime]]:
        """
        Найти ближайший свободный слот на РЦ длительностью duration_minutes, начиная с from_dt.
        Учитываются занятые интервалы и границы смен (операция не выходит за пределы смены).
        """
        if from_dt.tzinfo is None:
            from_dt = from_dt.replace(tzinfo=timezone.utc)
        busy = self._get_busy_intervals(work_center_id)
        duration_delta = timedelta(minutes=duration_minutes)

        if duration_minutes > MINUTES_PER_SHIFT:
            duration_minutes = MINUTES_PER_SHIFT
            duration_delta = timedelta(minutes=duration_minutes)

        shift_start, shift_end = self._get_shift_boundaries(from_dt)
        if from_dt < shift_start:
            current = shift_start
        else:
            current = from_dt

        max_iterations = 365 * 2 * 24
        for _ in range(max_iterations):
            shift_start, shift_end = self._get_shift_boundaries(current)
            if current < shift_start:
                current = shift_start
            slot_end = current + duration_delta
            if slot_end > shift_end:
                current = shift_end
                continue
            overlaps = any(
                (current < end and slot_end > start)
                for start, end in busy
            )
            if not overlaps:
                return (current, slot_end)
            current = slot_end

        return None

    def _plan_operations_for_order(
        self, order: ManufacturingOrder, reservation_result: ComponentReservationResult, mass_planning_info: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Запланировать операции производства для заказа (Этап 2).

        - Получает маршрут по product_id заказа.
        - Для каждой операции маршрута находит следующий свободный слот на РЦ с учётом смен.
        - При длительности операции больше 12 ч разбивает на две части (две смены).
        - Создаёт ProductionTask с planned временем (started_at/completed_at).
        - Если в BOM заказа есть Масса и её не хватает на остатке — создаёт задачи на варку массы (по маршруту массы).
        """
        route_data = self._get_route_and_operations(str(order.product_id))
        if not route_data:
            return []

        route, route_operations = route_data
        planned: List[Dict] = []
        # Начало планирования — от даты срока заказа или «сейчас»
        base_dt = order.due_date
        if base_dt and base_dt.tzinfo is None:
            base_dt = base_dt.replace(tzinfo=timezone.utc)
        if not base_dt or base_dt < datetime.now(timezone.utc):
            base_dt = datetime.now(timezone.utc)
        base_dt = self._align_to_shift_start(base_dt)

        order_quantity = float(order.quantity)

        # Проверяем, нужна ли варка массы: если в BOM заказа есть Масса и её не хватает на остатке,
        # то были зарезервированы компоненты массы, и нужно создать задачи на варку.
        try:
            fg_product_id = UUID(order.product_id)
            fg_bom_entries = (
                self.db.query(BillOfMaterial)
                .filter(BillOfMaterial.parent_product_id == fg_product_id)
                .all()
            )
            mass_product_id = None
            mass_required_qty = 0.0
            for bom_entry in fg_bom_entries:
                child_product = self.db.get(Product, bom_entry.child_product_id)
                if child_product and child_product.product_type == ProductType.BULK.value:
                    mass_product_id = bom_entry.child_product_id
                    mass_required_qty = float(bom_entry.quantity) * order_quantity
                    break

            # Если есть масса и её не хватает на остатке — планируем варку массы
            if mass_product_id and mass_required_qty > 0:
                mass_available = self._get_available_quantity(mass_product_id)
                mass_product = self.db.get(Product, mass_product_id)
                mass_product_name = (mass_product.product_name or mass_product.product_code or str(mass_product_id)) if mass_product else str(mass_product_id)
                
                # Собираем информацию о массе для анализа отсутствия задач на Реакторе
                mass_info = {
                    "mass_product_id": str(mass_product_id),
                    "mass_product_name": mass_product_name,
                    "order_id": str(order.id),
                    "order_number": order.order_number or "",
                    "required_qty": round(mass_required_qty, 4),
                    "available_qty": round(mass_available, 4),
                    "needs_production": mass_available < mass_required_qty,
                    "has_route": False,
                    "has_operations": False,
                    "route_id": None,
                    "operations_count": 0,
                }
                
                if mass_available < mass_required_qty:
                    # Нужна варка массы — получаем маршрут массы и планируем операции
                    mass_route_data = self._get_route_and_operations(str(mass_product_id))
                    
                    if not mass_route_data:
                        # Маршрут отсутствует - это критическая ошибка, блокируем планирование
                        raise MassRouteValidationError(
                            mass_product_id=mass_product_id,
                            mass_product_name=mass_product_name,
                            order_id=order.id,
                            order_number=order.order_number or "",
                            reason="отсутствует маршрут производства (ManufacturingRoute) в БД",
                        )
                    
                    mass_route, mass_route_operations = mass_route_data
                    mass_info["has_route"] = True
                    mass_info["route_id"] = str(mass_route.id)
                    
                    if not mass_route_operations:
                        # Операции отсутствуют - это критическая ошибка, блокируем планирование
                        raise MassRouteValidationError(
                            mass_product_id=mass_product_id,
                            mass_product_name=mass_product_name,
                            order_id=order.id,
                            order_number=order.order_number or "",
                            reason=f"в маршруте (ID: {mass_route.id}) отсутствуют операции (RouteOperation)",
                        )
                    
                    mass_info["has_operations"] = True
                    mass_info["operations_count"] = len(mass_route_operations)
                    
                    if mass_planning_info is not None:
                        mass_planning_info.append(mass_info)
                    
                    # Планируем операции варки массы
                    mass_base_dt = base_dt  # Варка должна быть раньше сборки ГП
                    for mass_route_op in mass_route_operations:
                        mass_duration = int(mass_route_op.estimated_duration_minutes or 60)
                        mass_wc_id = mass_route_op.work_center_id
                        mass_remaining = mass_duration
                        mass_slot_start = mass_base_dt
                        while mass_remaining > 0:
                            mass_chunk = min(mass_remaining, MINUTES_PER_SHIFT)
                            mass_slot = self._find_next_free_slot(mass_wc_id, mass_chunk, mass_slot_start)
                            if not mass_slot:
                                break
                            mass_start, mass_end = mass_slot
                            mass_task = ProductionTask(
                                order_id=order.id,
                                operation_id=mass_route_op.id,
                                work_center_id=mass_wc_id,
                                status=TaskStatus.QUEUED,
                                started_at=mass_start,
                                completed_at=mass_end,
                                quantity_kg=mass_required_qty,
                            )
                            self.db.add(mass_task)
                            self.db.flush()
                            planned.append({
                                "task_id": str(mass_task.id),
                                "order_id": str(order.id),
                                "operation_name": mass_route_op.operation_name,
                                "work_center_id": str(mass_wc_id),
                                "planned_start": mass_start.isoformat(),
                                "planned_end": mass_end.isoformat(),
                                "duration_minutes": mass_chunk,
                            })
                            mass_remaining -= mass_chunk
                            mass_slot_start = mass_end
                            mass_base_dt = mass_end
                        # После варки массы операции ГП начинаются позже (варка должна завершиться до начала сборки)
                        if mass_base_dt > base_dt:
                            base_dt = mass_base_dt
                else:
                    # Масса есть на остатке, варка не требуется
                    if mass_planning_info is not None:
                        mass_planning_info.append(mass_info)
        except MassRouteValidationError:
            # Пробрасываем ошибки валидации маршрутов масс наверх
            raise
        except (ValueError, TypeError, AttributeError):
            pass  # Если ошибка при проверке массы — продолжаем планирование ГП

        # Планируем операции ГП (после варки массы, если она была запланирована)
        for route_op in route_operations:
            duration_minutes = int(route_op.estimated_duration_minutes or 60)
            work_center_id = route_op.work_center_id

            remaining_minutes = duration_minutes
            slot_start = base_dt

            while remaining_minutes > 0:
                chunk_minutes = min(remaining_minutes, MINUTES_PER_SHIFT)
                slot = self._find_next_free_slot(work_center_id, chunk_minutes, slot_start)
                if not slot:
                    break
                start_dt, end_dt = slot

                task = ProductionTask(
                    order_id=order.id,
                    operation_id=route_op.id,
                    work_center_id=work_center_id,
                    status=TaskStatus.QUEUED,
                    started_at=start_dt,
                    completed_at=end_dt,
                )
                if order_quantity and order_quantity == int(order_quantity):
                    task.quantity_pcs = int(order_quantity)
                else:
                    task.quantity_kg = order_quantity
                self.db.add(task)
                self.db.flush()

                planned.append({
                    "task_id": str(task.id),
                    "order_id": str(order.id),
                    "operation_name": route_op.operation_name,
                    "work_center_id": str(work_center_id),
                    "planned_start": start_dt.isoformat(),
                    "planned_end": end_dt.isoformat(),
                    "duration_minutes": chunk_minutes,
                })

                remaining_minutes -= chunk_minutes
                slot_start = end_dt
                base_dt = end_dt

        if planned:
            self.db.commit()

        return planned
