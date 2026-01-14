# Domain Model v2.0 — Process Manufacturing для ДСИЗ

## Обзор

Система моделирует **гибридное (процессно-дискретное) производство** ДСИЗ:
- **Процессная часть:** варка массы (batch-процесс с параметрами).
- **Дискретная часть:** розлив, упаковка, маркировка (штучный учёт).

---

## Основные сущности

### 1. Product (Продукт/Материал)

**Назначение:** Универсальный справочник для сырья, массы, тары, ГП.

**Типы продуктов:**
- `RAW_MATERIAL` — сырьё (глицерин, масла, отдушки).
- `BULK` — масса (крем, паста, гель, мыло).
- `PACKAGING` — тара (туба, флакон, крышка, этикетка, гофроящик).
- `FINISHED_GOOD` — готовая продукция.

**Ключевые поля:**
- `product_code` — SKU/артикул (уникальный).
- `product_type` — тип продукта (enum).
- `unit_of_measure` — единица измерения (`kg`, `pcs`, `liters`).
- `min_batch_size_kg`, `batch_size_step_kg` — для BULK (кратность варки).
- `shelf_life_days` — срок хранения массы.

---

### 2. BillOfMaterial (BOM — спецификация состава)

**Назначение:** Многоуровневая BOM (3 уровня: ГП → Масса + Тара → Сырьё).

**Связи:**
- `parent_product_id` → что производим.
- `child_product_id` → что требуется (компонент).
- `quantity` — количество компонента на 1 единицу родителя.
- `unit` — единица измерения.

**Пример:**
ГП "Крем реген 100 мл" (1 шт)
├── Масса "Крем реген" (0.09 кг)
│ ├── Глицерин (0.015 кг)
│ ├── Стеариновая кислота (0.003 кг)
│ └── ...
├── Туба 100 мл (1 шт)
└── Гофроящик (0.02 шт — 1 ящик на 48 туб)

text

---

### 3. Batch (Производственная партия массы)

**Назначение:** Варка массы (batch-процесс).

**Статусы:**
- `PLANNED` — запланирована.
- `IN_PROGRESS` — выполняется.
- `COMPLETED` — завершена.
- `FAILED` — сбой.

**Ключевые поля:**
- `batch_number` — номер партии (уникальный).
- `product_id` — какую массу варим (FK → Product, тип BULK).
- `quantity_kg` — объём варки.
- `work_center_id` — реактор/куб.
- `parent_order_id` — из какого заказа создан batch (FK → ManufacturingOrder).

---

### 4. InventoryBalance (Остатки на складе)

**Назначение:** Учёт остатков массы, тары, ГП (упрощённая WMS).

**Ключевые поля:**
- `product_id` — что хранится.
- `location` — где (строка: `WAREHOUSE`, `CUB_1`, `ACCUMULATOR_A`, `SEMI_FG_ZONE`).
- `quantity` — количество.
- `product_status` — `FINISHED` (готовая продукция) или `SEMI_FINISHED` (полуфабрикат без маркировки).
- `production_date`, `expiry_date` — для массы (контроль срока годности).
- `reserved_quantity` — зарезервировано под заказы.

---

### 5. ManufacturingOrder (обновлённый)

**Новые поля:**
- `order_type` — `CUSTOMER` (клиентский) или `INTERNAL_BULK` (внутренний заказ на варку массы).
- `priority` — `URGENT` (<7 дней), `HIGH` (7-14), `NORMAL` (14-30), `LOW` (>30).
- `parent_order_id` — для зависимых заказов (варка массы под фасовку).
- `source_order_ids` (JSON) — список UUID заказов, объединённых в консолидированный план.
- `is_consolidated` — флаг консолидации.

**Статусы для ДСИЗ:**
- `SHIP` — заказ на отгрузку (высокий приоритет).
- `IN_WORK` — заказ в работе (низкий приоритет, используется для консолидации).

---

### 6. WorkCenter (обновлённый)

**Новые поля:**
- `batch_capacity_kg` — объём реактора/куба (1000 кг).
- `cycles_per_shift` — количество циклов за смену (2 варки/смену).
- `exclusive_products` (JSON) — список product_id, которые нельзя производить одновременно.
- `parallel_capacity` — сколько задач одновременно (4 куба параллельно).

**Производительность** задаётся через отдельную таблицу `WorkCenterCapacity`.

---

### 7. WorkCenterCapacity (НОВАЯ таблица)

**Назначение:** Хранит производительность WorkCenter по каждому продукту.

**Ключевые поля:**
- `work_center_id` — оборудование.
- `product_id` — продукт.
- `capacity_per_shift` — производительность за смену.
- `unit` — единица измерения (`pcs`, `kg`).

**Пример:**
Тубировочная машина → Крем 100 мл: 15000 шт/смена
Тубировочная машина → Крем 200 мл: 9000 шт/смена
Линия розлива мыла → Мыло 250 мл: 5000 шт/смена

text

---

### 8. ProductionTask (обновлённый)

**Новые поля:**
- `batch_id` — если задача связана с варкой массы (FK → Batch).
- `quantity_kg` — для batch-операций.
- `quantity_pcs` — для дискретных операций.

---

## Сервисы

### MRPService (Material Requirements Planning)

**Методы:**

1. **`consolidate_orders(horizon_days=30)`**
   - Собирает все заказы SHIP и IN_WORK с `due_date < today + horizon_days`.
   - Рассчитывает приоритет для SHIP заказов.
   - Группирует по `product_id`.
   - Проверяет capacity → добавляет IN_WORK заказы при наличии свободных мощностей.

2. **`explode_bom(product_id, quantity)`**
   - Рекурсивно обходит BOM.
   - Возвращает словарь потребностей: `{product_id: quantity}`.

3. **`calculate_net_requirement(product_id, gross_requirement)`**
   - Нетто = Потребность - Остаток на складе.

4. **`round_to_batch(product_id, net_requirement_kg)`**
   - Округляет до кратности варки (для массы).

5. **`create_dependent_bulk_order(parent_order_id, bulk_product_id, quantity_kg, due_date)`**
   - Создаёт заказ типа `INTERNAL_BULK` (зависимый от родительского).

---

## Связи (ER-диаграмма)

Product (1) ←──── (N) BillOfMaterial ────→ (1) Product
↓
├─ InventoryBalance (N)
├─ Batch (N)
├─ WorkCenterCapacity (N)
└─ ManufacturingOrder (N)

ManufacturingOrder (1) ←──── (N) ProductionTask
↓
└─── (N) Batch

WorkCenter (1) ←──── (N) WorkCenterCapacity ────→ (1) Product
↓
└─── (N) ProductionTask

text

---

## Бизнес-процесс (упрощённо)

1. **Создание клиентского заказа** (статус SHIP):
   - `ManufacturingOrder` с `order_type=CUSTOMER`, `status=SHIP`, `due_date`.

2. **Консолидация заказов** (`MRPService.consolidate_orders()`):
   - Группировка по продукту.
   - Расчёт приоритета.
   - Добавление IN_WORK заказов (если есть мощности).

3. **Взрыв BOM** (`MRPService.explode_bom()`):
   - Определение потребности в массе и таре.

4. **Расчёт нетто-потребности**:
   - Проверка остатков на складе (`InventoryBalance`).
   - Нетто = Потребность - Остаток.

5. **Округление до кратности варки** (для массы):
   - Например, нужно 1200 кг → планируем 2×1000 кг.

6. **Создание зависимого заказа на варку** (INTERNAL_BULK):
   - `ManufacturingOrder` с `order_type=INTERNAL_BULK`, `parent_order_id`.

7. **Создание Batch**:
   - `Batch` с привязкой к заказу и Work Center (реактор).

8. **Диспетчеризация задач**:
   - Создание `ProductionTask` для варки, розлива, маркировки.

9. **Выполнение**:
   - Варка массы → обновление `InventoryBalance` (BULK).
   - Розлив → создание полуфабриката (`product_status=SEMI_FINISHED`).
   - Маркировка → перевод в `product_status=FINISHED`.

10. **Отгрузка**:
    - Уменьшение `InventoryBalance` (FINISHED).

---

## Changelog

**v2.0 (2026-01-14):**
- Добавлены сущности: `Product`, `BillOfMaterial`, `Batch`, `InventoryBalance`, `WorkCenterCapacity`.
- Расширены: `ManufacturingOrder` (приоритеты, консолидация), `WorkCenter` (batch-поля), `ProductionTask` (batch_id, quantity_kg).
- Добавлен `MRPService` для планирования.
- Добавлен учёт полуфабрикатов (`product_status=SEMI_FINISHED`).

**v1.0 (2026-01-13):**
- Базовая модель для дискретного производства.