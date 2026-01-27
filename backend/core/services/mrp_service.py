"""
MRP (Material Requirements Planning) Service.

Обрабатывает:
- Консолидацию заказов
- Взрыв BOM
- Расчёт нетто-потребности
- Округление до кратности варки
- Создание зависимых заказов на варку
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.product import Product
from backend.core.models.bill_of_material import BillOfMaterial
from backend.core.models.inventory_balance import InventoryBalance
from backend.core.models.enums import (
    OrderStatus, OrderType, OrderPriority,
    ProductType, ProductStatus
)
from backend.config.factory_config import get_factory_config


class MRPService:
    """Сервис планирования потребности в материалах (MRP)."""
    
    def __init__(self, db: Session):
        """
        Инициализация MRP сервиса.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
    
    def consolidate_orders(
        self, 
        horizon_days: Optional[int] = None
    ) -> List[Dict]:
        """
        Консолидация клиентских заказов в пределах горизонта планирования.
        
        Группирует заказы по продукту, рассчитывает приоритеты и опционально
        добавляет IN_WORK заказы при наличии свободных мощностей.
        
        Args:
            horizon_days: Горизонт планирования в днях (если None, используется значение из конфигурации)
        
        Returns:
            Список консолидированных планов заказов со структурой:
            [
                {
                    "product_id": UUID,
                    "product_code": str,
                    "product_name": str,
                    "total_quantity": float,
                    "priority": str,
                    "earliest_due_date": datetime,
                    "latest_due_date": datetime,
                    "source_orders": [UUID, ...],
                    "order_count": int
                },
                ...
            ]
        
        Бизнес-правила:
            - Учитываются только SHIP и IN_WORK заказы
            - Расчёт приоритета для SHIP заказов:
              - <7 дней: URGENT
              - 7-14 дней: HIGH
              - 14-30 дней: NORMAL
              - >30 дней: LOW
            - IN_WORK заказы добавляются только при наличии мощностей (MVP: всегда добавляются)
        """
        config = get_factory_config()
        horizon = horizon_days or config.planning.mrp_horizon_days
        cutoff_date = datetime.utcnow() + timedelta(days=horizon)
        
        # Получаем SHIP заказы в пределах горизонта
        ship_orders = self.db.query(ManufacturingOrder).filter(
            ManufacturingOrder.status == OrderStatus.SHIP,
            ManufacturingOrder.due_date <= cutoff_date
        ).all()
        
        # Получаем IN_WORK заказы
        in_work_orders = self.db.query(ManufacturingOrder).filter(
            ManufacturingOrder.status == OrderStatus.IN_WORK
        ).all()
        
        # Группируем по продукту
        product_map: Dict[str, Dict] = {}
        
        for order in ship_orders:
            # product_id в ManufacturingOrder - это String, нужно конвертировать в UUID
            product_id_str = str(order.product_id)
            
            if product_id_str not in product_map:
                # Пытаемся найти продукт по UUID или строке
                product_uuid = None
                product = None
                
                try:
                    product_uuid = UUID(product_id_str) if product_id_str else None
                    if product_uuid:
                        product = self.db.query(Product).filter(
                            Product.id == product_uuid
                        ).first()
                except (ValueError, AttributeError):
                    # Если не удалось конвертировать в UUID, пытаемся найти продукт по коду
                    pass
                
                # Если продукт не найден, пропускаем этот заказ (или используем значения по умолчанию)
                if not product:
                    # Для MVP: пропускаем заказы с невалидными product_id
                    continue
                
                product_map[product_id_str] = {
                    "product_id": product.id,  # Всегда UUID из модели Product
                    "product_code": product.product_code,
                    "product_name": product.product_name,
                    "total_quantity": 0,
                    "priority": None,
                    "earliest_due_date": None,
                    "latest_due_date": None,
                    "source_orders": [],
                    "order_count": 0
                }
            
            product_data = product_map[product_id_str]
            product_data["total_quantity"] += float(order.quantity)
            product_data["source_orders"].append(order.id)
            product_data["order_count"] += 1
            
            # Отслеживаем самую раннюю и самую позднюю дату выполнения
            if product_data["earliest_due_date"] is None or order.due_date < product_data["earliest_due_date"]:
                product_data["earliest_due_date"] = order.due_date
            
            if product_data["latest_due_date"] is None or order.due_date > product_data["latest_due_date"]:
                product_data["latest_due_date"] = order.due_date
            
            # Рассчитываем приоритет на основе самой ранней даты выполнения
            days_until_due = (order.due_date - datetime.utcnow()).days
            order_priority = self._calculate_priority(days_until_due)
            
            # Используем наивысший приоритет (URGENT > HIGH > NORMAL > LOW)
            if product_data["priority"] is None or self._priority_rank(order_priority) > self._priority_rank(product_data["priority"]):
                product_data["priority"] = order_priority
        
        # TODO: Добавить IN_WORK заказы при наличии мощностей (MVP: пропускаем проверку мощностей)
        # Для MVP просто консолидируем SHIP заказы
        
        return list(product_map.values())
    
    def explode_bom(
        self, 
        product_id: UUID, 
        quantity: float,
        level: int = 0,
        max_levels: int = 10
    ) -> Dict[UUID, float]:
        """
        Рекурсивный взрыв BOM для расчёта потребности в материалах.
        
        Args:
            product_id: Продукт для взрыва
            quantity: Требуемое количество
            level: Текущий уровень рекурсии (для безопасности)
            max_levels: Максимальная глубина рекурсии
        
        Returns:
            Словарь, сопоставляющий product_id требуемому количеству:
            {
                UUID("raw-material-1"): 15.5,
                UUID("packaging-1"): 1000,
                ...
            }
        
        Примечания:
            - Возвращает компоненты на ВСЕХ уровнях (не только прямые дочерние)
            - Обрабатывает многоуровневые BOM (ГП → BULK → RAW)
            - Обнаруживает циклические зависимости (защита max_levels)
        """
        if level >= max_levels:
            raise ValueError(f"Взрыв BOM превысил максимальный уровень ({max_levels}). Возможна циклическая зависимость.")
        
        requirements: Dict[UUID, float] = {}
        
        # Получаем записи BOM для этого продукта
        bom_entries = self.db.query(BillOfMaterial).filter(
            BillOfMaterial.parent_product_id == product_id
        ).all()
        
        for bom in bom_entries:
            child_quantity = float(bom.quantity) * quantity
            
            # Добавляем этот компонент в требования
            if bom.child_product_id in requirements:
                requirements[bom.child_product_id] += child_quantity
            else:
                requirements[bom.child_product_id] = child_quantity
            
            # Рекурсивно взрываем BOM дочернего продукта
            child_requirements = self.explode_bom(
                bom.child_product_id, 
                child_quantity,
                level + 1,
                max_levels
            )
            
            # Объединяем требования дочерних продуктов
            for child_id, child_qty in child_requirements.items():
                if child_id in requirements:
                    requirements[child_id] += child_qty
                else:
                    requirements[child_id] = child_qty
        
        return requirements
    
    def calculate_net_requirement(
        self, 
        product_id: UUID, 
        gross_requirement: float
    ) -> float:
        """
        Расчёт нетто-потребности (валовая - доступный запас).
        
        Args:
            product_id: Продукт для проверки
            gross_requirement: Валовая потребность
        
        Returns:
            Нетто-потребность (валовая - доступный)
            Возвращает 0, если достаточно запаса
        
        Бизнес-правила:
            - Доступный = quantity - reserved_quantity
            - Учитывается только инвентарь со статусом FINISHED
            - Нетто не может быть отрицательным
        """
        # Получаем доступный инвентарь (только FINISHED)
        inventories = self.db.query(InventoryBalance).filter(
            InventoryBalance.product_id == product_id,
            InventoryBalance.product_status == ProductStatus.FINISHED
        ).all()
        
        total_available = sum(
            float(inv.quantity) - float(inv.reserved_quantity)
            for inv in inventories
        )
        
        net_requirement = gross_requirement - total_available
        
        return max(0, net_requirement)
    
    def round_to_batch(
        self, 
        product_id: UUID, 
        net_requirement_kg: float
    ) -> float:
        """
        Округление потребности в массе до кратности варки.
        
        Args:
            product_id: BULK продукт
            net_requirement_kg: Нетто-потребность в кг
        
        Returns:
            Округлённое количество (кратное batch_size_step_kg)
        
        Бизнес-правила:
            - Применяется только к BULK продуктам
            - Округляет ВВЕРХ до следующего кратного batch_size_step_kg
            - Обеспечивает >= min_batch_size_kg
            - Пример: нужно 1200 кг, шаг 1000 кг → 2000 кг (2 батча)
        
        Raises:
            ValueError: Если продукт не является типом BULK
        """
        config = get_factory_config()
        
        # Check if batch rounding is enabled
        if not config.planning.batch_rounding:
            return net_requirement_kg
        
        product = self.db.query(Product).filter(
            Product.id == product_id
        ).first()
        
        if not product:
            raise ValueError(f"Продукт {product_id} не найден")
        
        if product.product_type != ProductType.BULK.value:
            raise ValueError(f"Продукт {product.product_code} не является типом BULK")
        
        if not product.batch_size_step_kg:
            raise ValueError(f"Продукт {product.product_code} не имеет определённого batch_size_step_kg")
        
        # Обеспечиваем минимальный размер батча
        # Use product-specific batch size or default from config
        min_batch = float(product.min_batch_size_kg or config.planning.default_batch_size_kg)
        if net_requirement_kg < min_batch:
            return min_batch
        
        # Округляем вверх до следующего кратного batch_size_step_kg
        batch_step = float(product.batch_size_step_kg)
        batches_needed = -(-net_requirement_kg // batch_step)  # Деление с округлением вверх
        
        return batches_needed * batch_step
    
    def create_dependent_bulk_order(
        self,
        bulk_product_id: UUID,
        quantity_kg: float,
        due_date: datetime,
        parent_order_id: Optional[UUID] = None
    ) -> ManufacturingOrder:
        """
        Создание зависимого INTERNAL_BULK заказа на варку массы.
        
        Args:
            bulk_product_id: BULK продукт для варки
            quantity_kg: Количество для варки (уже округлено до батча)
            due_date: Дата выполнения
            parent_order_id: Родительский заказ (опционально, для зависимых заказов)
        
        Returns:
            Созданный ManufacturingOrder
        
        Бизнес-правила:
            - order_type = INTERNAL_BULK
            - status = PLANNED
            - parent_order_id связывает с родителем (если указан)
            - Дата выполнения = указанная дата
        """
        product = self.db.query(Product).filter(
            Product.id == bulk_product_id
        ).first()
        
        if not product:
            raise ValueError(f"Продукт {bulk_product_id} не найден")
        
        if product.product_type != ProductType.BULK.value:
            raise ValueError(f"Продукт {product.product_code} не является типом BULK")
        
        # Генерируем номер заказа
        order_count = self.db.query(ManufacturingOrder).filter(
            ManufacturingOrder.order_type == OrderType.INTERNAL_BULK.value
        ).count()
        order_number = f"BULK-{datetime.utcnow().strftime('%Y%m%d')}-{order_count + 1:04d}"
        
        # Создаём заказ
        # Примечание: product_id в ManufacturingOrder - это String, конвертируем UUID в строку
        order = ManufacturingOrder(
            order_number=order_number,
            product_id=str(bulk_product_id),  # Конвертируем UUID в строку
            quantity=quantity_kg,
            status=OrderStatus.PLANNED,
            order_type=OrderType.INTERNAL_BULK.value,
            parent_order_id=parent_order_id,  # Может быть None
            due_date=due_date
        )
        
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        
        return order
    
    # ========================================================================
    # Вспомогательные методы
    # ========================================================================
    
    def _calculate_priority(self, days_until_due: int) -> str:
        """Расчёт приоритета заказа на основе дней до выполнения."""
        if days_until_due < 7:
            return OrderPriority.URGENT.value
        elif days_until_due < 14:
            return OrderPriority.HIGH.value
        elif days_until_due < 30:
            return OrderPriority.NORMAL.value
        else:
            return OrderPriority.LOW.value
    
    def _priority_rank(self, priority: str) -> int:
        """Возвращает ранг приоритета (больше = более срочно)."""
        ranks = {
            OrderPriority.URGENT.value: 4,
            OrderPriority.HIGH.value: 3,
            OrderPriority.NORMAL.value: 2,
            OrderPriority.LOW.value: 1
        }
        return ranks.get(priority, 0)
