## 3. Data Model & DB Customization (Модель данных и БД)

### 3.1. Принципы

**Core-модели неизменны**: 

- `ManufacturingOrder`, `ProductionTask`, `WorkCenter`, `Product`, `BOM`, `Batch`, `Inventory` и др. остаются базовыми.
- DSIZ-специфика — **минимальные расширения**:
  - новые справочные таблицы,
  - поля в существующих таблицах (Alembic),
  - JSONB для гибкости.

**Этапы внедрения данных:**

1. **MVP:** Python-константы + `config/dsiz_config.yaml` (gitignored).
2. **Phase 2:** миграция в БД (Alembic).
3. **Phase 3:** админка для редактирования.

***

### 3.2. Новые таблицы (справочники DSIZ)

#### 3.2.1. `dsiz_work_center_modes`

Режимы реактора.

```sql
CREATE TABLE dsiz_work_center_modes (
    id SERIAL PRIMARY KEY,
    work_center_id UUID NOT NULL REFERENCES work_centers(id),
    mode_name VARCHAR(50) NOT NULL, -- 'CREAM_MODE', 'PASTE_MODE'
    min_load_kg DECIMAL(10,2) NOT NULL,
    max_load_kg DECIMAL(10,2) NOT NULL,
    cycle_duration_hours INTEGER NOT NULL, -- 4 or 5
    max_cycles_per_shift INTEGER NOT NULL DEFAULT 2,
    created_at TIMESTAMP DEFAULT NOW()
);
-- UNIQUE(work_center_id, mode_name)
```

#### 3.2.2. `dsiz_changeover_matrix`

Матрица совместимости.

```sql
CREATE TABLE dsiz_changeover_matrix (
    id SERIAL PRIMARY KEY,
    from_compatibility_group VARCHAR(100) NOT NULL,
    to_compatibility_group VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL, -- 'COMPATIBLE', 'INCOMPATIBLE', 'UNIVERSAL'
    setup_time_minutes INTEGER NOT NULL DEFAULT 0,
    UNIQUE(from_compatibility_group, to_compatibility_group)
);
```

#### 3.2.3. `dsiz_base_rates`

Базовые скорости операций.

```sql
CREATE TABLE dsiz_base_rates (
    id SERIAL PRIMARY KEY,
    product_sku VARCHAR(50) NOT NULL,
    work_center_id UUID REFERENCES work_centers(id),
    base_rate_units_per_hour DECIMAL(10,2) NOT NULL,
    is_human_dependent BOOLEAN DEFAULT FALSE
);
```

#### 3.2.4. `dsiz_workforce_requirements`

Нормы укомплектованности.

```sql
CREATE TABLE dsiz_workforce_requirements (
    id SERIAL PRIMARY KEY,
    work_center_id UUID REFERENCES work_centers(id),
    role_name VARCHAR(50) NOT NULL, -- 'OPERATOR', 'PACKER'
    required_count INTEGER NOT NULL,
    is_mandatory BOOLEAN NOT NULL DEFAULT TRUE,
    min_count_for_degraded_mode INTEGER,
    degradation_factor DECIMAL(3,2), -- 0.5 при 3/4 операторах
    UNIQUE(work_center_id, role_name)
);
```

#### 3.2.5. `dsiz_labeling_rules`

Правила маркировки.

```sql
CREATE TABLE dsiz_labeling_rules (
    id SERIAL PRIMARY KEY,
    work_center_id UUID REFERENCES work_centers(id),
    default_mode VARCHAR(10) NOT NULL, -- 'AUTO', 'MANUAL'
    auto_printer_installed BOOLEAN NOT NULL,
    manual_fallback_allowed BOOLEAN NOT NULL DEFAULT TRUE,
    qr_availability_policy VARCHAR(20) DEFAULT 'DELAY_LABELING' -- 'DELAY_LABELING', 'BLOCK_RELEASE'
);
```

#### 3.2.6. `dsiz_qr_availability`

Доступность QR-кодов **по задачам** (партиям).

```sql
CREATE TABLE dsiz_qr_availability (
    id SERIAL PRIMARY KEY,
    production_task_id UUID REFERENCES production_tasks(id),
    qr_ready_date TIMESTAMP,
    qr_count INTEGER,
    status VARCHAR(20) DEFAULT 'PENDING' -- 'PENDING', 'READY', 'ISSUED'
);
```

#### 3.2.7. `dsiz_product_work_center_routing`

```sql
CREATE TABLE dsiz_product_work_center_routing (
    id SERIAL PRIMARY KEY,
    product_sku VARCHAR(50) NOT NULL,
    work_center_id UUID REFERENCES work_centers(id),
    is_allowed BOOLEAN NOT NULL DEFAULT TRUE,
    min_quantity_for_wc INTEGER,        -- напр. 5000 для авто
    priority_order INTEGER DEFAULT 1,   -- авто > полуавто
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(product_sku, work_center_id)
);
```
Примеры начальных данных:

```text
Спрей100мл, WC_AUTO_LIQUID_SOAP, TRUE, 5000, 1
Спрей100мл, WC_SEMI_AUTO_FILLING, TRUE, NULL, 2
Паста200мл, WC_TUBE_LINE_1, TRUE, NULL, 1
Паста200мл, WC_SEMI_AUTO_FILLING, FALSE, NULL, NULL
```

***

### 3.3. Расширения существующих таблиц

#### 3.3.1. `work_centers`

```sql
ALTER TABLE work_centers ADD COLUMN dsiz_concurrency_limit INTEGER DEFAULT 1;
ALTER TABLE work_centers ADD COLUMN dsiz_max_cycles_per_shift INTEGER DEFAULT 2;
ALTER TABLE work_centers ADD COLUMN dsiz_is_reactor BOOLEAN DEFAULT FALSE;
ALTER TABLE work_centers ADD COLUMN dsiz_is_human_dependent BOOLEAN DEFAULT FALSE;
```

#### 3.3.2. `products`

```sql
ALTER TABLE products ADD COLUMN dsiz_compatibility_group VARCHAR(100);
ALTER TABLE products ADD COLUMN dsiz_shelf_life_days INTEGER DEFAULT 30; -- Bulk
ALTER TABLE products ADD COLUMN dsiz_product_type VARCHAR(20); -- 'BULK', 'FG', 'TARA', 'RAW_MATERIAL'
```

#### 3.3.3. `manufacturing_orders`

```sql
ALTER TABLE manufacturing_orders ADD COLUMN dsiz_labeling_mode VARCHAR(10) DEFAULT 'MANUAL';
```

#### 3.3.4. `production_tasks`

```sql
ALTER TABLE production_tasks ADD COLUMN dsiz_reactor_slot INTEGER; -- 1 or 2
ALTER TABLE production_tasks ADD COLUMN dsiz_setup_time_minutes INTEGER DEFAULT 0; -- из changeover
```

***

### 3.4. DSIZ-конфигурация (MVP)

`config/dsiz_config.yaml` (gitignored, загружается сервисами):

```yaml
reactor:
  max_cycles_per_shift: 2
  cip_schedule: "monday_shift_1"

workforce:
  auto_liquid_soap:
    operators: 4
    min_degraded: 3
    degradation_factor: 0.5

labeling:
  default_mode: "MANUAL"
  qr_policy: "DELAY_LABELING"

changeover:
  matrix_file: "dsiz_changeover.csv"
```

***

### 3.5. План миграций Alembic

**001 — MVP расширения:**
```bash
alembic revision --autogenerate -m "dsiz_mvp_extensions"
alembic upgrade head
```

**002 — Справочники:**
```bash
alembic revision --autogenerate -m "dsiz_master_data_tables"
alembic upgrade head
```

**003 — Полная конфигурация в БД:**
```bash
alembic revision --autogenerate -m "dsiz_full_config_in_db"
```

***

### 3.6. Начальные данные (MVP)

Скрипты:
- `dsiz_work_center_modes.sql`
- `dsiz_base_rates.csv` (для 4 SKU)
- `dsiz_changeover_matrix.csv`
- `dsiz_workforce_requirements.sql`

Команды деплоя:
```bash
ssh root@185.177.94.29
cd /root/mes-platform
git pull origin develop
alembic upgrade head
psql -d supabase_db -f migrations/dsiz_initial_data.sql
docker compose restart
```

***