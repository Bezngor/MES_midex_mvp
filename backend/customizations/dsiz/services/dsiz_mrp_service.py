"""
DSIZ MRP Service.

Расширение базового MRPService для специфики DSIZ:
- Расчёт нетто-потребности с учётом остатков Bulk (shelf_life=30 дней)
- Планирование варок реактора с учётом CIP, лимитов, under-loading, режимов
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.core.services.mrp_service import MRPService
from backend.core.models.manufacturing_order import ManufacturingOrder
from backend.core.models.product import Product
from backend.core.models.bill_of_material import BillOfMaterial
from backend.core.models.inventory_balance import InventoryBalance
from backend.core.models.enums import (
    OrderStatus, OrderType, ProductType, ProductStatus
)
from backend.customizations.dsiz.services.dsiz_workforce_service import DSIZWorkforceService


class NetRequirement(BaseModel):
    """Результат расчёта нетто-потребности."""
    fg_sku: str
    gross_requirement_kg: float
    bulk_available_kg: float
    net_requirement_kg: float
    bulk_product_sku: Optional[str] = None


class BatchOrder(BaseModel):
    """План варки реактора."""
    bulk_product_sku: str
    quantity_kg: float
    mode: str  # 'CREAM_MODE' or 'PASTE_MODE'
    shift_date: date
    shift_num: int
    reactor_slot: int  # 1 or 2


class DSIZMRPService(MRPService):
    """
    DSIZ-специфичный MRP сервис.
    
    Наследует базовый MRPService и добавляет:
    - Расчёт нетто-потребности для ГП с учётом остатков Bulk (shelf_life=30 дней)
    - Планирование варок реактора с учётом CIP, лимитов, under-loading, режимов
    """
    
    def __init__(self, db: Session):
        """
        Инициализация DSIZ MRP сервиса.
        
        Args:
            db: Сессия базы данных
        """
        super().__init__(db)
        self.workforce = DSIZWorkforceService(db)
        self._load_dsiz_config()
    
    def _load_dsiz_config(self) -> None:
        """Загрузка DSIZ конфигурации из YAML (MVP)."""
        import yaml
        from pathlib import Path
        
        config_paths = [
            Path("./config/dsiz_config.yaml"),
            Path("./backend/config/dsiz_config.yaml"),
        ]
        
        self.config = {}
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        self.config = yaml.safe_load(f) or {}
                    break
                except Exception as e:
                    print(f"⚠️  Ошибка загрузки конфига {config_path}: {e}")
        
        # Дефолтные значения для MVP
        if not self.config:
            self.config = {
                'reactor': {
                    'max_cycles_per_shift': 2,
                    'cip_schedule': 'monday_shift_1'
                },
                'work_center_modes': {},
                'product_routing': {}
            }
    
    def calculate_net_requirement(
        self, 
        fg_sku: str, 
        horizon_days: int
    ) -> NetRequirement:
        """
        Расчёт нетто-потребности для ГП с учётом остатков Bulk (shelf_life=30 дней).
        
        Args:
            fg_sku: SKU готового продукта
            horizon_days: Горизонт планирования в днях
        
        Returns:
            NetRequirement с расчётом нетто-потребности
        
        Бизнес-правила:
            1. Собираем заказы ГП в пределах горизонта
            2. Взрываем BOM для получения потребности в Bulk (масса)
            3. Учитываем остатки Bulk со сроком годности >= horizon_days (shelf_life=30 дней)
            4. Рассчитываем нетто-потребность
        """
        # 1. Получаем продукт ГП
        fg_product = self.db.query(Product).filter(
            Product.product_code == fg_sku
        ).first()
        
        if not fg_product:
            raise ValueError(f"Продукт ГП {fg_sku} не найден")
        
        if fg_product.product_type != ProductType.FINISHED_GOOD.value:
            raise ValueError(f"Продукт {fg_sku} не является типом FINISHED_GOOD")
        
        # 2. Собираем заказы ГП в пределах горизонта
        cutoff_date = datetime.utcnow() + timedelta(days=horizon_days)
        fg_orders = self.db.query(ManufacturingOrder).filter(
            ManufacturingOrder.product_id == str(fg_product.id),
            ManufacturingOrder.status.in_([OrderStatus.SHIP, OrderStatus.IN_WORK]),
            ManufacturingOrder.due_date <= cutoff_date
        ).all()
        
        # 3. Рассчитываем валовую потребность в ГП
        gross_requirement_fg = sum(float(order.quantity) for order in fg_orders)
        
        # 4. Взрываем BOM для получения потребности в Bulk (масса)
        bulk_requirements: Dict[UUID, float] = {}
        
        # Ищем BOM записи, где родитель = ГП, дочерний = Bulk
        bom_entries = self.db.query(BillOfMaterial).filter(
            BillOfMaterial.parent_product_id == fg_product.id
        ).all()
        
        for bom in bom_entries:
            child_product = self.db.query(Product).filter(
                Product.id == bom.child_product_id
            ).first()
            
            if child_product and child_product.product_type == ProductType.BULK.value:
                # Конвертируем количество ГП в массу Bulk
                bulk_quantity_kg = float(bom.quantity) * gross_requirement_fg
                
                if bom.child_product_id in bulk_requirements:
                    bulk_requirements[bom.child_product_id] += bulk_quantity_kg
                else:
                    bulk_requirements[bom.child_product_id] = bulk_quantity_kg
        
        # 5. Рассчитываем доступные остатки Bulk (с учётом shelf_life=30 дней)
        bulk_available_kg = 0.0
        bulk_product_sku = None
        
        if bulk_requirements:
            # Берём первый Bulk продукт (в MVP предполагаем один Bulk на ГП)
            bulk_product_id = list(bulk_requirements.keys())[0]
            bulk_product = self.db.query(Product).filter(
                Product.id == bulk_product_id
            ).first()
            
            if bulk_product:
                bulk_product_sku = bulk_product.product_code
                
                # Получаем остатки Bulk со сроком годности >= horizon_days
                # shelf_life = 30 дней по умолчанию
                shelf_life_days = int(bulk_product.shelf_life_days or 30)
                min_expiry_date = datetime.utcnow() + timedelta(days=horizon_days + shelf_life_days)
                
                bulk_inventories = self.db.query(InventoryBalance).filter(
                    InventoryBalance.product_id == bulk_product_id,
                    InventoryBalance.product_status == ProductStatus.FINISHED,
                    InventoryBalance.expiry_date >= min_expiry_date
                ).all()
                
                bulk_available_kg = sum(
                    float(inv.available_quantity)
                    for inv in bulk_inventories
                )
        
        # 6. Рассчитываем нетто-потребность
        gross_requirement_kg = sum(bulk_requirements.values())
        net_requirement_kg = max(0, gross_requirement_kg - bulk_available_kg)
        
        return NetRequirement(
            fg_sku=fg_sku,
            gross_requirement_kg=gross_requirement_kg,
            bulk_available_kg=bulk_available_kg,
            net_requirement_kg=net_requirement_kg,
            bulk_product_sku=bulk_product_sku
        )
    
    def plan_reactor_batches(
        self, 
        mass_demand: Dict[str, float], 
        shift_date: date, 
        shift_num: int
    ) -> List[BatchOrder]:
        """
        Планирование варок реактора на смену.
        
        Args:
            mass_demand: Словарь {bulk_sku: required_kg}
            shift_date: Дата смены
            shift_num: Номер смены (1 или 2)
        
        Returns:
            Список BatchOrder для планирования варок
        
        Бизнес-правила:
            1. Проверка CIP (monday shift 1 = [])
            2. Лимит 2 варки/смену
            3. Under-loading (min из dsiz_work_center_modes)
            4. Режимы CREAM_MODE/PASTE_MODE
        """
        # 1. Проверка CIP (monday shift 1 = [])
        if shift_date.weekday() == 0 and shift_num == 1:  # Понедельник, смена 1
            cip_schedule = self.config.get('reactor', {}).get('cip_schedule', 'monday_shift_1')
            if cip_schedule == 'monday_shift_1':
                return []  # CIP - нет варок
        
        # 2. Лимит 2 варки/смену
        max_cycles = self.config.get('reactor', {}).get('max_cycles_per_shift', 2)
        
        # 3. Получаем режимы реактора из конфига
        work_center_modes = self.config.get('work_center_modes', {})
        reactor_modes = work_center_modes.get('WC_REACTOR_MAIN', {})
        
        # 4. Планируем варки
        batch_orders: List[BatchOrder] = []
        slot = 1
        
        for bulk_sku, required_kg in mass_demand.items():
            if slot > max_cycles:
                break  # Лимит варок достигнут
            
            # Определяем режим (CREAM_MODE или PASTE_MODE)
            mode = self._determine_reactor_mode(bulk_sku, reactor_modes)
            
            # Получаем min_load_kg для режима
            min_load_kg = self._get_min_load_for_mode(mode, reactor_modes)
            
            # Проверка under-loading
            if required_kg < min_load_kg:
                # Under-loading: округляем до минимума
                batch_quantity_kg = min_load_kg
            else:
                # Округляем до кратности batch_size_step_kg
                bulk_product = self.db.query(Product).filter(
                    Product.product_code == bulk_sku
                ).first()
                
                if bulk_product and bulk_product.batch_size_step_kg:
                    batch_step = float(bulk_product.batch_size_step_kg)
                    batches_needed = -(-required_kg // batch_step)  # Округление вверх
                    batch_quantity_kg = batches_needed * batch_step
                else:
                    batch_quantity_kg = required_kg
            
            batch_orders.append(BatchOrder(
                bulk_product_sku=bulk_sku,
                quantity_kg=batch_quantity_kg,
                mode=mode,
                shift_date=shift_date,
                shift_num=shift_num,
                reactor_slot=slot
            ))
            
            slot += 1
        
        return batch_orders
    
    def _determine_reactor_mode(self, bulk_sku: str, reactor_modes: Dict) -> str:
        """
        Определение режима реактора для Bulk продукта.
        
        Args:
            bulk_sku: SKU Bulk продукта
            reactor_modes: Конфигурация режимов реактора
        
        Returns:
            'CREAM_MODE' или 'PASTE_MODE'
        """
        # В MVP: определяем по названию продукта или используем дефолт
        bulk_product = self.db.query(Product).filter(
            Product.product_code == bulk_sku
        ).first()
        
        if bulk_product:
            product_name_lower = bulk_product.product_name.lower()
            if 'крем' in product_name_lower or 'cream' in product_name_lower:
                return 'CREAM_MODE'
            elif 'паста' in product_name_lower or 'paste' in product_name_lower:
                return 'PASTE_MODE'
        
        # Дефолт: PASTE_MODE
        return 'PASTE_MODE'
    
    def _get_min_load_for_mode(self, mode: str, reactor_modes: Dict) -> float:
        """
        Получение минимальной загрузки для режима реактора.
        
        Args:
            mode: Режим ('CREAM_MODE' или 'PASTE_MODE')
            reactor_modes: Конфигурация режимов реактора
        
        Returns:
            Минимальная загрузка в кг
        """
        mode_config = reactor_modes.get(mode, {})
        min_load_kg = mode_config.get('min_load_kg', 750.0)  # Дефолт: 750 кг
        
        return float(min_load_kg)
