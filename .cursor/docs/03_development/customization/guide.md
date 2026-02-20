# MES Platform — Customization Guide

**Версия:** 2.1.0  
**Дата:** 19 января 2026  
**Для разработчиков:** Python (FastAPI + SQLAlchemy)

---

## 🎯 Цель документа

Этот гайд показывает, **как безопасно кастомизировать MES Platform** под специфику вашего завода без изменения кода в `backend/core/`.

**Принцип кастомизации:**
- ✅ **DO:** Расширяйте логику через наследование в `backend/customizations/`
- ✅ **DO:** Переопределяйте методы сервисов через Dependency Injection
- ❌ **DON'T:** Изменяйте файлы в `backend/core/` напрямую
- ❌ **DON'T:** Хардкодите factory-specific данные в код

---

## 📂 Структура customizations/

```
backend/customizations/
├── __init__.py                  # Exports для DI
├── README.md                    # Документация кастомизаций
├── services/                    # Переопределённые сервисы
│   ├── __init__.py
│   ├── custom_mrp_service.py   # Пример: Custom MRP logic
│   └── custom_dispatching_service.py # Пример: Priority dispatching
├── models/                      # Расширения моделей (опционально)
│   ├── __init__.py
│   └── custom_order.py         # Пример: Extra fields для Order
├── routes/                      # Дополнительные endpoints (опционально)
│   ├── __init__.py
│   └── custom_reports.py       # Пример: Factory-specific reports
└── integrations/                # Интеграции с внешними системами
    ├── __init__.py
    ├── erp_integration.py      # Пример: Sync с 1С/SAP
    └── iot_integration.py      # Пример: IoT датчики на оборудовании
```

---

## 🔧 Механизм кастомизации: Dependency Injection

MES Platform использует **FastAPI Dependency Injection** для замены сервисов:

### Пример: Заменить MRPService на CustomMRPService

**1. Создать custom сервис в `backend/customizations/services/`:**

```python
# backend/customizations/services/custom_mrp_service.py
from backend.core.services.mrp_service import MRPService
from uuid import UUID
from datetime import datetime

class CustomMRPService(MRPService):
    """
    Custom MRP logic: exclude expired inventory from available stock.
    """
    
    def calculate_net_requirement(
        self, 
        product_id: UUID, 
        gross_requirement: float
    ) -> float:
        """
        Override: исключить просроченный инвентарь из available stock.
        """
        # Вызвать базовый метод
        net = super().calculate_net_requirement(product_id, gross_requirement)
        
        # Дополнительная логика: вычесть expired inventory
        expired_qty = self._get_expired_inventory(product_id)
        net = max(0, net + expired_qty)
        
        return net
    
    def _get_expired_inventory(self, product_id: UUID) -> float:
        """
        Helper: рассчитать просроченный инвентарь.
        """
        from backend.core.models.inventory_balance import InventoryBalance
        
        expired = self.session.query(InventoryBalance).filter(
            InventoryBalance.product_id == product_id,
            InventoryBalance.expiry_date < datetime.utcnow()
        ).all()
        
        return sum(item.quantity for item in expired)
```

**2. Зарегистрировать в `backend/customizations/__init__.py`:**

```python
# backend/customizations/__init__.py
from backend.customizations.services.custom_mrp_service import CustomMRPService

__all__ = ["CustomMRPService"]
```

**3. Применить Dependency Override в `backend/src/main.py`:**

```python
# backend/src/main.py
from fastapi import FastAPI
from backend.core.services.mrp_service import MRPService
from backend.customizations import CustomMRPService

app = FastAPI()

# Dependency Injection: заменить MRPService на CustomMRPService
app.dependency_overrides[MRPService] = CustomMRPService

# Теперь все endpoints, использующие MRPService, будут использовать CustomMRPService
```

**4. Проверка:**

```bash
# Запустить тесты
pytest backend/tests/test_custom_mrp_service.py

# Проверить в production
curl -X POST https://your-domain.com/api/v1/mrp/consolidate \
  -H "Content-Type: application/json" \
  -d '{"horizon_days": 7}'
```

---

## 📚 Типичные сценарии кастомизации

### Сценарий 1: Приоритетная диспетчеризация

**Задача:** URGENT заказы должны диспетчеризоваться раньше NORMAL, даже если NORMAL был создан раньше.

**Решение:**

```python
# backend/customizations/services/priority_dispatching_service.py
from backend.core.services.dispatching_service import DispatchingService
from backend.core.models.production_task import ProductionTask, TaskStatus
from backend.core.models.manufacturing_order import ManufacturingOrder
from uuid import UUID

class PriorityDispatchingService(DispatchingService):
    """
    Custom dispatching: sort by order priority (URGENT > HIGH > NORMAL > LOW).
    """
    
    def get_next_queued_task(self, work_center_id: UUID) -> ProductionTask | None:
        """
        Override: сортировать по приоритету заказа, затем по FIFO.
        """
        tasks = self.session.query(ProductionTask)\
            .filter(
                ProductionTask.status == TaskStatus.QUEUED,
                ProductionTask.work_center_id == work_center_id
            )\
            .join(ManufacturingOrder)\
            .order_by(
                ManufacturingOrder.priority.desc(),  # URGENT first
                ProductionTask.created_at.asc()       # FIFO within priority
            )\
            .all()
        
        return tasks if tasks else None
```

**Применение в main.py:**

```python
from backend.core.services.dispatching_service import DispatchingService
from backend.customizations.services.priority_dispatching_service import PriorityDispatchingService

app.dependency_overrides[DispatchingService] = PriorityDispatchingService
```

**Тестирование:**

```python
# backend/tests/test_priority_dispatching.py
def test_urgent_order_dispatched_first(db_session):
    service = PriorityDispatchingService(db_session)
    
    # Создать NORMAL заказ (раньше по времени)
    order_normal = create_test_order(
        priority="NORMAL", 
        created_at=datetime(2026, 1, 19, 8, 0)
    )
    task_normal = create_test_task(order_id=order_normal.id, status="QUEUED")
    
    # Создать URGENT заказ (позже по времени)
    order_urgent = create_test_order(
        priority="URGENT", 
        created_at=datetime(2026, 1, 19, 9, 0)
    )
    task_urgent = create_test_task(order_id=order_urgent.id, status="QUEUED")
    
    # Проверка: URGENT должен быть выбран первым
    next_task = service.get_next_queued_task(work_center_id)
    assert next_task.id == task_urgent.id
```

---

### Сценарий 2: Запрет одновременной варки несовместимых продуктов

**Задача:** Нельзя варить "Крем с отдушкой A" и "Крем с отдушкой B" одновременно (риск перекрёстного загрязнения).

**Решение:**

```python
# backend/customizations/services/batch_conflict_service.py
from backend.core.services.dispatching_service import DispatchingService
from backend.core.models.product import Product
from backend.core.models.production_task import ProductionTask, TaskStatus
from uuid import UUID
from typing import List

class BatchConflictDispatchingService(DispatchingService):
    """
    Custom dispatching: check for incompatible products running simultaneously.
    """
    
    # Конфигурация несовместимых групп (можно вынести в factory_config.yaml)
    INCOMPATIBLE_GROUPS = [
        ["PRODUCT_A_FRAGRANCE_1", "PRODUCT_B_FRAGRANCE_2"],
        ["PRODUCT_C_COLOR_RED", "PRODUCT_D_COLOR_BLUE"]
    ]
    
    def dispatch_task(
        self, 
        task_id: UUID, 
        work_center_id: UUID, 
        scheduled_start: datetime
    ):
        """
        Override: проверить конфликты перед диспетчеризацией.
        """
        task = self.session.query(ProductionTask).get(task_id)
        product = self.session.query(Product).get(task.product_id)
        
        # Проверить активные задачи на несовместимость
        if self._has_conflict(product.product_code):
            raise ValueError(
                f"Cannot dispatch task {task_id}: "
                f"incompatible product {product.product_code} is already running"
            )
        
        # Если конфликта нет — вызвать базовый метод
        return super().dispatch_task(task_id, work_center_id, scheduled_start)
    
    def _has_conflict(self, product_code: str) -> bool:
        """
        Helper: проверить, есть ли активные несовместимые продукты.
        """
        # Найти группу несовместимости для product_code
        conflict_group = None
        for group in self.INCOMPATIBLE_GROUPS:
            if product_code in group:
                conflict_group = group
                break
        
        if not conflict_group:
            return False  # Нет ограничений
        
        # Проверить активные задачи
        active_tasks = self.session.query(ProductionTask)\
            .filter(ProductionTask.status == TaskStatus.IN_PROGRESS)\
            .join(Product)\
            .filter(Product.product_code.in_(conflict_group))\
            .all()
        
        # Конфликт есть, если активна задача по другому продукту из группы
        return any(
            task.product.product_code != product_code 
            for task in active_tasks
        )
```

**Применение:**

```python
app.dependency_overrides[DispatchingService] = BatchConflictDispatchingService
```

---

### Сценарий 3: Интеграция с ERP (1С/SAP)

**Задача:** Синхронизировать заказы из ERP в MES при создании.

**Решение:**

```python
# backend/customizations/integrations/erp_integration.py
import requests
from backend.core.models.manufacturing_order import ManufacturingOrder
from uuid import UUID

class ERPIntegration:
    """
    Integration with 1C/SAP ERP system.
    """
    
    def __init__(self, erp_base_url: str, api_key: str):
        self.erp_base_url = erp_base_url
        self.api_key = api_key
    
    def sync_order_to_erp(self, order: ManufacturingOrder):
        """
        Отправить заказ в ERP после создания в MES.
        """
        payload = {
            "order_number": order.order_number,
            "product_code": order.product.product_code,
            "quantity": order.quantity,
            "due_date": order.due_date.isoformat(),
            "status": order.status.value
        }
        
        response = requests.post(
            f"{self.erp_base_url}/api/v1/manufacturing-orders",
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        
        if response.status_code != 201:
            raise Exception(f"ERP sync failed: {response.text}")
        
        return response.json()
```

**Использование в custom route:**

```python
# backend/customizations/routes/custom_orders.py
from fastapi import APIRouter, Depends
from backend.core.routes.orders import create_order as core_create_order
from backend.customizations.integrations.erp_integration import ERPIntegration

router = APIRouter()

@router.post("/api/v1/orders")
def create_order_with_erp_sync(order_data: dict, db: Session = Depends(get_db)):
    """
    Override: создать заказ + синхронизировать с ERP.
    """
    # Создать заказ через core logic
    order = core_create_order(order_data, db)
    
    # Синхронизировать с ERP
    erp = ERPIntegration(
        erp_base_url="https://erp.myfactory.com",
        api_key="your-api-key"
    )
    erp.sync_order_to_erp(order)
    
    return order
```

**Регистрация route в main.py:**

```python
from backend.customizations.routes.custom_orders import router as custom_orders_router

app.include_router(custom_orders_router)
```

---

### Сценарий 4: Учёт простоев оборудования (Downtime Tracking)

**Задача:** Записывать простои Work Center (поломка, ТО, отсутствие материалов).

**Решение:**

**1. Расширить модель WorkCenter (через миграцию):**

```python
# backend/customizations/models/downtime.py
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from backend.src.db.base import Base
import uuid

class WorkCenterDowntime(Base):
    __tablename__ = "work_center_downtimes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    work_center_id = Column(UUID(as_uuid=True), ForeignKey("work_centers.id"))
    downtime_start = Column(DateTime, nullable=False)
    downtime_end = Column(DateTime, nullable=True)  # NULL если ещё не завершён
    reason = Column(String, nullable=False)  # "MAINTENANCE", "BREAKDOWN", "NO_MATERIAL"
    notes = Column(Text, nullable=True)
```

**2. Создать миграцию:**

```bash
cd backend
alembic revision -m "add_work_center_downtimes_table"
```

**3. Создать API endpoint:**

```python
# backend/customizations/routes/downtime.py
from fastapi import APIRouter, Depends
from backend.customizations.models.downtime import WorkCenterDowntime
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

router = APIRouter()

class DowntimeCreate(BaseModel):
    work_center_id: UUID
    downtime_start: datetime
    reason: str
    notes: str | None = None

@router.post("/api/v1/downtimes")
def create_downtime(data: DowntimeCreate, db: Session = Depends(get_db)):
    """
    Зарегистрировать простой оборудования.
    """
    downtime = WorkCenterDowntime(**data.dict())
    db.add(downtime)
    db.commit()
    return downtime

@router.get("/api/v1/downtimes")
def list_downtimes(work_center_id: UUID | None = None, db: Session = Depends(get_db)):
    """
    Получить список простоев (с фильтром по Work Center).
    """
    query = db.query(WorkCenterDowntime)
    if work_center_id:
        query = query.filter(WorkCenterDowntime.work_center_id == work_center_id)
    return query.all()
```

**4. Зарегистрировать в main.py:**

```python
from backend.customizations.routes.downtime import router as downtime_router
app.include_router(downtime_router, tags=["Customizations"])
```

---

## 🧪 Тестирование кастомизаций

### Подход к тестированию

**1. Unit тесты для custom сервисов:**

```python
# backend/tests/customizations/test_priority_dispatching.py
import pytest
from backend.customizations.services.priority_dispatching_service import PriorityDispatchingService
from backend.core.models.manufacturing_order import ManufacturingOrder, OrderPriority

@pytest.fixture
def custom_service(db_session):
    return PriorityDispatchingService(db_session)

def test_urgent_priority_over_fifo(custom_service, db_session):
    # Create NORMAL order (earlier timestamp)
    order_normal = ManufacturingOrder(
        order_number="TEST-001",
        priority=OrderPriority.NORMAL,
        created_at=datetime(2026, 1, 19, 8, 0)
    )
    db_session.add(order_normal)
    
    # Create URGENT order (later timestamp)
    order_urgent = ManufacturingOrder(
        order_number="TEST-002",
        priority=OrderPriority.URGENT,
        created_at=datetime(2026, 1, 19, 9, 0)
    )
    db_session.add(order_urgent)
    db_session.commit()
    
    # Dispatch should pick URGENT first
    next_task = custom_service.get_next_queued_task(work_center_id)
    assert next_task.order_id == order_urgent.id
```

**2. Integration тесты:**

```python
# backend/tests/customizations/test_erp_integration.py
def test_order_synced_to_erp(client, mock_erp_api):
    """
    Test: заказ синхронизируется с ERP после создания.
    """
    # Mock ERP API response
    mock_erp_api.post("/api/v1/manufacturing-orders", status_code=201)
    
    # Create order via MES API
    response = client.post("/api/v1/orders", json={
        "product_id": "uuid-product-001",
        "quantity": 1000,
        "due_date": "2026-01-25T12:00:00Z"
    })
    
    assert response.status_code == 201
    
    # Verify ERP API was called
    assert mock_erp_api.called
```

**3. Запуск тестов:**

```bash
# Только custom тесты
pytest backend/tests/customizations/ -v

# Все тесты (core + customizations)
pytest backend/tests/ --cov=backend --cov-report=html
```

---

## 📖 Best Practices

### 1. Документирование кастомизаций

Создайте `backend/customizations/README.md`:

```markdown
# Factory-Specific Customizations

## Active Customizations

### 1. Priority Dispatching Service
- **File:** `services/priority_dispatching_service.py`
- **Purpose:** Диспетчеризация по приоритету заказа (URGENT > NORMAL)
- **Applied in:** `main.py` (DI override)
- **Tests:** `tests/customizations/test_priority_dispatching.py`

### 2. ERP Integration (1C)
- **File:** `integrations/erp_integration.py`
- **Purpose:** Синхронизация заказов с 1С
- **Endpoint:** `POST /api/v1/orders` (overridden)
- **Tests:** `tests/customizations/test_erp_integration.py`

## Configuration

Custom логика использует `config/factory_config.yaml`:

```yaml
customizations:
  priority_dispatching:
    enabled: true
  erp_integration:
    enabled: true
    base_url: "https://erp.myfactory.com"
    api_key: "${ERP_API_KEY}"  # from .env
```
```

---

### 2. Версионирование кастомизаций

**Git workflow:**

```bash
# Создать ветку для кастомизации
git checkout -b feature/priority-dispatching

# Коммитить в customizations/
git add backend/customizations/services/priority_dispatching_service.py
git commit -m "feat(customizations): add priority dispatching service"

# Merge в develop (не в template-base!)
git checkout develop
git merge feature/priority-dispatching
```

---

### 3. Изоляция от core обновлений

**Правило:** Обновления `backend/core/` из `template-base` НЕ должны ломать `backend/customizations/`.

**Проверка перед merge:**

```bash
# Обновить core из template-base
git fetch origin template-base
git merge origin/template-base

# Запустить все тесты (core + customizations)
pytest backend/tests/ -v

# Если тесты fail — исправить customizations
```

---

### 4. Конфигурация через YAML

**Вместо:**

```python
# ❌ BAD: Hardcoded values
class CustomMRPService(MRPService):
    HORIZON_DAYS = 14  # Hardcoded!
```

**Используйте:**

```python
# ✅ GOOD: Config from YAML
from backend.config.factory_config import get_factory_config

class CustomMRPService(MRPService):
    def __init__(self, session):
        super().__init__(session)
        config = get_factory_config()
        self.horizon_days = config["mrp"]["horizon_days"]
```

---

## 🔗 Связь с другими документами

- **TEMPLATE_GUIDE.md** — общий обзор шаблона
- **REPOSITORY_STRUCTURE.md** — структура `backend/customizations/`
- **DOMAIN_MODEL.md** — описание сервисов (MRP, Dispatching)
- **API_SPEC.md** — endpoints для расширения
- **TESTING.md** — как писать тесты для customizations

---

## ❓ FAQ

**Q: Можно ли изменять файлы в `backend/core/`?**  
A: ❌ **НЕТ.** Это нарушает принцип template. Используйте наследование в `backend/customizations/`.

---

**Q: Как обновить core из template-base, если есть customizations?**  
A:

```bash
# 1. Создать резервную ветку
git checkout -b backup-before-update

# 2. Merge из template-base
git checkout develop
git merge origin/template-base

# 3. Запустить тесты
pytest backend/tests/

# 4. Если есть конфликты — исправить в customizations/
```

---

**Q: Можно ли добавлять новые таблицы в БД?**  
A: ✅ **ДА.** Создавайте модели в `backend/customizations/models/` и миграции через Alembic:

```bash
alembic revision -m "add_custom_table_xyz"
```

---

**Q: Как передавать конфигурацию в custom сервисы?**  
A: Через `backend.config.factory_config.get_factory_config()`:

```python
from backend.config.factory_config import get_factory_config

class CustomService:
    def __init__(self):
        self.config = get_factory_config()
        self.enabled = self.config["customizations"]["my_feature"]["enabled"]
```

---

## 📞 Поддержка

**Вопросы по кастомизации:**
- **GitHub Issues:** https://github.com/Bezngor/MES_midex/issues
- **Email:** support@your-company.com

**Платная кастомизация:**
- Разработка custom логики под ваш завод (1-2 недели)
- Code review ваших customizations
- Обучение команды паттернам кастомизации

---

**Версия документа:** 1.0  
**Последнее обновление:** 19 января 2026  
**Автор:** MES Development Team

**Следующий шаг:** Начните с простых кастомизаций (config → services → routes → models).
