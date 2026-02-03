"""
Сервис стратегического планирования производства.

Реализует алгоритм пересчёта плана производства на основе принятых заказов покупателей.
См. STRATEGIC_PLANNING_ALGORITHM.md для детального описания алгоритма.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_

from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.bill_of_material import BillOfMaterial
from backend.core.models.inventory_balance import InventoryBalance
from backend.core.models.product import Product
from backend.core.models.production_task import ProductionTask
from backend.core.models.work_center import WorkCenter
from backend.core.models.enums import OrderPriority, ProductStatus, ProductType, TaskStatus
from backend.core.services.mrp_service import MRPService


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

        # Разделяем на успешные и неуспешные
        successful_orders = [
            order_id
            for order_id, result in reservation_results.items()
            if result.success
        ]
        failed_orders = [
            {
                "order_id": str(result.order_id),
                "missing_components": {
                    str(comp_id): qty for comp_id, qty in result.missing_components.items()
                },
            }
            for result in reservation_results.values()
            if not result.success
        ]

        # Этап 2: Планирование операций производства (по приоритетам)
        planned_operations = []

        for priority in [OrderPriority.URGENT, OrderPriority.HIGH, OrderPriority.NORMAL, OrderPriority.LOW]:
            priority_orders = [
                order
                for order in orders_by_priority[priority]
                if order.id in successful_orders
            ]
            for order in priority_orders:
                operations = self._plan_operations_for_order(order, reservation_results[order.id])
                planned_operations.extend(operations)

        return {
            "success": True,
            "reserved_orders": [str(oid) for oid in successful_orders],
            "failed_orders": failed_orders,
            "planned_operations": planned_operations,
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

    def _plan_operations_for_order(
        self, order: ManufacturingOrder, reservation_result: ComponentReservationResult
    ) -> List[Dict]:
        """
        Запланировать операции производства для заказа.

        TODO: Реализовать полный алгоритм планирования с учётом:
        - Проверки наличия Массы на остатке
        - Поиска существующих операций с таким же ГП
        - Резервирования времени РЦ/реактора
        - Разделения операций между сменами
        - Расчёта времени изготовления
        """
        # Заглушка - будет реализована в следующей итерации
        return []
