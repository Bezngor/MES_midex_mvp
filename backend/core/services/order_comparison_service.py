"""
Сервис для сравнения производственных заказов и выявления изменений.

Реализует шаг бизнес-процесса "Блок обновления данных" → "Выявить новые и/или измененные ЗП".
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_

from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.order_snapshot import OrderSnapshot
from backend.core.models.enums import OrderType


class OrderComparisonService:
    """Сервис для сравнения заказов и выявления изменений."""

    def __init__(self, db: Session):
        """
        Инициализация сервиса.

        Args:
            db: SQLAlchemy сессия базы данных
        """
        self.db = db

    def create_snapshot(
        self,
        order: ManufacturingOrder,
        snapshot_type: str = "MANUAL",
        notes: Optional[str] = None
    ) -> OrderSnapshot:
        """
        Создать снимок состояния заказа.

        Args:
            order: Производственный заказ
            snapshot_type: Тип снимка (MANUAL, AUTO, SYNC)
            notes: Дополнительные заметки

        Returns:
            Созданный снимок
        """
        # Формируем полный JSON снимок для детального сравнения
        full_snapshot = {
            "order_number": order.order_number,
            "product_id": order.product_id,
            "quantity": float(order.quantity),
            "status": order.status.value if hasattr(order.status, 'value') else str(order.status),
            "due_date": order.due_date.isoformat() if order.due_date else None,
            "order_type": order.order_type,
            "priority": order.priority,
            "source_status": order.source_status,
            "parent_order_id": str(order.parent_order_id) if order.parent_order_id else None,
            "source_order_ids": [str(oid) for oid in order.source_order_ids] if order.source_order_ids else None,
            "is_consolidated": order.is_consolidated,
        }

        snapshot = OrderSnapshot(
            order_id=order.id,
            order_number=order.order_number,
            product_id=order.product_id,
            quantity=order.quantity,
            status=order.status.value if hasattr(order.status, 'value') else str(order.status),
            due_date=order.due_date,
            order_type=order.order_type,
            priority=order.priority,
            source_status=order.source_status,
            parent_order_id=order.parent_order_id,
            source_order_ids=order.source_order_ids,
            is_consolidated=order.is_consolidated,
            snapshot_date=datetime.utcnow(),
            snapshot_type=snapshot_type,
            notes=notes,
            full_snapshot=full_snapshot,
        )

        self.db.add(snapshot)
        self.db.flush()
        return snapshot

    def create_snapshots_for_all_orders(
        self,
        order_type: Optional[str] = None,
        snapshot_type: str = "AUTO",
        notes: Optional[str] = None
    ) -> List[OrderSnapshot]:
        """
        Создать снимки для всех заказов (или заказов определённого типа).

        Args:
            order_type: Тип заказа для фильтрации (CUSTOMER, INTERNAL_BULK) или None для всех
            snapshot_type: Тип снимка
            notes: Дополнительные заметки

        Returns:
            Список созданных снимков
        """
        query = select(ManufacturingOrder)
        if order_type:
            query = query.where(ManufacturingOrder.order_type == order_type)

        orders = self.db.execute(query).scalars().all()
        snapshots = []

        for order in orders:
            snapshot = self.create_snapshot(order, snapshot_type=snapshot_type, notes=notes)
            snapshots.append(snapshot)

        self.db.commit()
        return snapshots

    def get_latest_snapshot(self, order_id: UUID) -> Optional[OrderSnapshot]:
        """
        Получить последний снимок заказа по UUID (для обратной совместимости).

        Args:
            order_id: ID заказа

        Returns:
            Последний снимок или None
        """
        query = (
            select(OrderSnapshot)
            .where(OrderSnapshot.order_id == order_id)
            .order_by(OrderSnapshot.snapshot_date.desc())
            .limit(1)
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def get_latest_snapshot_by_order_number(
        self, order_number: str, order_type: str
    ) -> Optional[OrderSnapshot]:
        """
        Получить последний снимок заказа по order_number и order_type.
        
        Используется для сравнения при синхронизации с 1С, где заказы идентифицируются
        по бизнес-номеру (order_number), а не по внутреннему UUID.

        Args:
            order_number: Номер заказа (бизнес-идентификатор из 1С)
            order_type: Тип заказа (CUSTOMER, INTERNAL_BULK)

        Returns:
            Последний снимок или None
        """
        query = (
            select(OrderSnapshot)
            .where(
                OrderSnapshot.order_number == order_number,
                OrderSnapshot.order_type == order_type
            )
            .order_by(OrderSnapshot.snapshot_date.desc())
            .limit(1)
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def identify_new_orders(
        self,
        since_date: Optional[datetime] = None,
        order_type: Optional[str] = OrderType.CUSTOMER.value
    ) -> List[ManufacturingOrder]:
        """
        Выявить новые заказы (заказы, для которых нет снимков).
        
        Сравнение выполняется по order_number + order_type (бизнес-идентификатор),
        а не по UUID, так как при синхронизации с 1С тот же order_number может
        получить новый UUID.

        Args:
            since_date: Дата, с которой искать новые заказы (если None, то все заказы без снимков)
            order_type: Тип заказа (по умолчанию CUSTOMER)

        Returns:
            Список новых заказов
        """
        # Получаем все заказы указанного типа
        query = select(ManufacturingOrder).where(ManufacturingOrder.order_type == order_type)
        
        if since_date:
            query = query.where(ManufacturingOrder.created_at >= since_date)

        all_orders = self.db.execute(query).scalars().all()

        # Находим заказы, для которых нет снимков по order_number
        new_orders = []
        for order in all_orders:
            latest_snapshot = self.get_latest_snapshot_by_order_number(
                order.order_number, 
                order.order_type
            )
            if latest_snapshot is None:
                new_orders.append(order)

        return new_orders

    def identify_changed_orders(
        self,
        since_date: Optional[datetime] = None,
        order_type: Optional[str] = OrderType.CUSTOMER.value
    ) -> List[Tuple[ManufacturingOrder, OrderSnapshot, Dict[str, Tuple]]]:
        """
        Выявить изменённые заказы (заказы, которые изменились с момента последнего снимка).
        
        Сравнение выполняется по order_number + order_type (бизнес-идентификатор),
        а не по UUID, так как при синхронизации с 1С тот же order_number может
        получить новый UUID.

        Args:
            since_date: Дата, с которой искать изменения (если None, то сравниваем с последним снимком)
            order_type: Тип заказа (по умолчанию CUSTOMER)

        Returns:
            Список кортежей (текущий заказ, последний снимок, словарь изменений)
            Словарь изменений: {поле: (старое_значение, новое_значение)}
        """
        # Получаем все заказы указанного типа
        query = select(ManufacturingOrder).where(ManufacturingOrder.order_type == order_type)
        all_orders = self.db.execute(query).scalars().all()

        changed_orders = []

        for order in all_orders:
            # Ищем снимок по order_number, а не по order_id
            latest_snapshot = self.get_latest_snapshot_by_order_number(
                order.order_number,
                order.order_type
            )
            
            if latest_snapshot is None:
                # Нет снимка - это новый заказ, пропускаем
                continue

            # Проверяем, был ли заказ изменён после снимка
            if since_date and latest_snapshot.snapshot_date < since_date:
                # Снимок старше since_date, но заказ мог измениться
                if order.updated_at and order.updated_at > latest_snapshot.snapshot_date:
                    changes = self._compare_order_with_snapshot(order, latest_snapshot)
                    if changes:
                        changed_orders.append((order, latest_snapshot, changes))
            else:
                # Сравниваем текущее состояние с последним снимком
                changes = self._compare_order_with_snapshot(order, latest_snapshot)
                if changes:
                    changed_orders.append((order, latest_snapshot, changes))

        return changed_orders

    def identify_deleted_orders(
        self,
        since_date: Optional[datetime] = None,
        order_type: Optional[str] = OrderType.CUSTOMER.value
    ) -> List[OrderSnapshot]:
        """
        Выявить удалённые заказы (заказы, которые есть в снимках, но отсутствуют в таблице).
        
        Сравнение выполняется по order_number + order_type (бизнес-идентификатор),
        а не по UUID, так как при синхронизации с 1С тот же order_number может
        получить новый UUID.

        Args:
            since_date: Дата, с которой искать удаления (если None, то все снимки)
            order_type: Тип заказа (по умолчанию CUSTOMER)

        Returns:
            Список снимков удалённых заказов (последний снимок для каждого order_number)
        """
        # Получаем все существующие заказы указанного типа
        existing_orders_query = select(ManufacturingOrder.order_number).where(
            ManufacturingOrder.order_type == order_type
        )
        existing_order_numbers = set(
            self.db.execute(existing_orders_query).scalars().all()
        )

        # Получаем все уникальные order_number из снимков
        # Для каждого order_number берём последний снимок
        from sqlalchemy import distinct, func
        
        # Подзапрос: последний снимок для каждого order_number
        subquery = (
            select(
                OrderSnapshot.order_number,
                func.max(OrderSnapshot.snapshot_date).label('max_date')
            )
            .where(OrderSnapshot.order_type == order_type)
            .group_by(OrderSnapshot.order_number)
            .subquery()
        )

        # Получаем последние снимки для каждого order_number
        latest_snapshots_query = (
            select(OrderSnapshot)
            .join(
                subquery,
                (OrderSnapshot.order_number == subquery.c.order_number) &
                (OrderSnapshot.snapshot_date == subquery.c.max_date)
            )
            .where(OrderSnapshot.order_type == order_type)
        )

        if since_date:
            latest_snapshots_query = latest_snapshots_query.where(
                OrderSnapshot.snapshot_date >= since_date
            )

        all_snapshots = self.db.execute(latest_snapshots_query).scalars().all()

        # Находим снимки, для которых нет соответствующего заказа
        deleted_snapshots = []
        for snapshot in all_snapshots:
            if snapshot.order_number not in existing_order_numbers:
                deleted_snapshots.append(snapshot)

        return deleted_snapshots

    def _compare_order_with_snapshot(
        self,
        order: ManufacturingOrder,
        snapshot: OrderSnapshot
    ) -> Dict[str, Tuple]:
        """
        Сравнить текущее состояние заказа со снимком.

        Args:
            order: Текущий заказ
            snapshot: Снимок для сравнения

        Returns:
            Словарь изменений: {поле: (старое_значение, новое_значение)}
        """
        changes = {}

        # Сравниваем поля
        if snapshot.product_id != order.product_id:
            changes["product_id"] = (snapshot.product_id, order.product_id)

        if float(snapshot.quantity) != float(order.quantity):
            changes["quantity"] = (float(snapshot.quantity), float(order.quantity))

        snapshot_status = snapshot.status
        order_status = order.status.value if hasattr(order.status, 'value') else str(order.status)
        if snapshot_status != order_status:
            changes["status"] = (snapshot_status, order_status)

        if snapshot.due_date != order.due_date:
            changes["due_date"] = (snapshot.due_date.isoformat() if snapshot.due_date else None,
                                   order.due_date.isoformat() if order.due_date else None)

        if snapshot.order_type != order.order_type:
            changes["order_type"] = (snapshot.order_type, order.order_type)

        if snapshot.priority != order.priority:
            changes["priority"] = (snapshot.priority, order.priority)

        if snapshot.source_status != order.source_status:
            changes["source_status"] = (snapshot.source_status, order.source_status)

        if snapshot.parent_order_id != order.parent_order_id:
            changes["parent_order_id"] = (
                str(snapshot.parent_order_id) if snapshot.parent_order_id else None,
                str(order.parent_order_id) if order.parent_order_id else None
            )

        if snapshot.is_consolidated != order.is_consolidated:
            changes["is_consolidated"] = (snapshot.is_consolidated, order.is_consolidated)

        return changes

    def get_order_changes(self, order_id: UUID) -> Optional[Dict]:
        """
        Получить детали изменений конкретного заказа по UUID.

        Args:
            order_id: ID заказа

        Returns:
            Словарь с информацией об изменениях или None, если заказ не найден или не изменялся
        """
        order = self.db.get(ManufacturingOrder, order_id)
        if not order:
            return None

        # Ищем снимок по order_number для корректного сравнения при синхронизации
        latest_snapshot = self.get_latest_snapshot_by_order_number(
            order.order_number,
            order.order_type
        )
        if not latest_snapshot:
            return {
                "order_id": str(order_id),
                "order_number": order.order_number,
                "product_id": str(order.product_id),
                "is_new": True,
                "is_changed": False,
                "is_deleted": False,
                "changes": None,
            }

        changes = self._compare_order_with_snapshot(order, latest_snapshot)
        if not changes:
            return None

        return {
            "order_id": str(order_id),
            "order_number": order.order_number,
            "product_id": str(order.product_id),
            "is_new": False,
            "is_changed": True,
            "is_deleted": False,
            "last_snapshot_date": latest_snapshot.snapshot_date.isoformat(),
            "current_updated_at": order.updated_at.isoformat() if order.updated_at else None,
            "changes": changes,
        }
