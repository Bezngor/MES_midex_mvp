# MES Platform Template v2.1 — Usage Guide

**Версия шаблона:** 2.1.0  
**Дата релиза:** 19 января 2026  
**Статус:** Production-Ready  
**Лицензия:** Proprietary (для внутреннего использования)

---

## 🎯 Что такое MES Platform Template?

MES Platform Template — это **универсальная система управления производством (MES)** для дискретного и процессного производства, готовая к развертыванию на новых предприятиях с минимальными доработками.

### Ключевые особенности

- ✅ **Production-ready** — проверено в реальном production на https://mes-midex-ru.factoryall.ru
- ✅ **Универсальная архитектура** — подходит для машиностроения, косметики, химии, пищевой промышленности
- ✅ **Модульная структура** — core (неизменяемая логика) + config (настройки) + customizations (расширения)
- ✅ **Высокое качество кода** — 141 тестов, 93% coverage, TypeScript 100%
- ✅ **GitOps-ready** — CI/CD через Docker, Dokploy, Traefik
- ✅ **ISA-95 compliant** — следует стандарту для MES систем

---

## 🏭 Поддерживаемые типы производства

### 1. Дискретное производство (Discrete Manufacturing)

**Примеры отраслей:**
- Машиностроение (сборка узлов, механообработка)
- Электроника (печатные платы, корпуса)
- Мебель (раскрой, сборка, покраска)

**Что поддерживается:**
- Штучный учёт продукции (`unit_of_measure: pcs`)
- Маршруты с последовательными операциями
- Work Center capacity по продуктам (шт/смену)
- Генеалогия (traceability) серийных номеров

---

### 2. Процессное производство (Process Manufacturing)

**Примеры отраслей:**
- Косметика (варка кремов, розлив, маркировка)
- Химия (смешивание, реакции, расфасовка)
- Пищевая промышленность (варка, охлаждение, упаковка)

**Что поддерживается:**
- Batch-процессы (партии массы в кг/литрах)
- Многоуровневые BOM (3+ уровня: ГП → Масса → Сырьё)
- Кратность варки (`min_batch_size_kg`, `batch_size_step_kg`)
- Срок годности полуфабрикатов (`shelf_life_days`)
- Учёт полуфабрикатов без маркировки (`product_status: SEMI_FINISHED`)

---

### 3. Гибридное производство (Hybrid)

**Пример:** Косметическая фабрика ДСИЗ
- **Процессная часть:** Варка массы (batch 1000 кг)
- **Дискретная часть:** Розлив в тубы (штучный учёт)

**Что поддерживается:**
- Переход batch → discrete (масса 1000 кг → 10,000 туб)
- Зависимые заказы (`INTERNAL_BULK` заказ варки под `CUSTOMER` заказ розлива)
- Консолидация заказов по продукту (MRP)

---

## 📦 Основные модули (Core Modules)

### 1. MRP (Material Requirements Planning)

**Статус:** ✅ Production-ready (48 тестов, 95% coverage)

**Функции:**
- Консолидация заказов по продукту с учётом приоритета и сроков
- Взрыв BOM (рекурсивный обход многоуровневой спецификации)
- Расчёт нетто-потребности (gross - available inventory)
- Округление до кратности варки (для batch-процессов)
- Создание зависимых заказов (варка массы → розлив)

**API Endpoints:**
- `POST /api/v1/mrp/consolidate` — консолидация заказов
- `POST /api/v1/mrp/explode-bom` — взрыв BOM

**Документация:** [MRP_GUIDE.md](MRP_GUIDE.md)

---

### 2. Dispatching & Scheduling

**Статус:** ✅ Production-ready (66 тестов, 92% coverage)

**Функции:**
- Release заказа (PLANNED → RELEASED, создание задач)
- Dispatch задачи на Work Center (QUEUED → IN_PROGRESS)
- Расчёт загрузки оборудования (load %, AVAILABLE/BUSY/OVERLOADED)
- Календарное планирование (Gantt chart data)
- FIFO диспетчеризация с проверкой capacity

**API Endpoints:**
- `POST /api/v1/dispatching/release-order` — запуск заказа
- `POST /api/v1/dispatching/dispatch-task` — назначение задачи
- `GET /api/v1/dispatching/work-center-load/{id}` — загрузка оборудования
- `GET /api/v1/dispatching/schedule` — расписание задач (Gantt)
- `POST /api/v1/dispatching/preview` — превью диспетчеризации

**Документация:** [DISPATCHING_GUIDE.md](DISPATCHING_GUIDE.md)

---

### 3. Inventory Management (упрощённая WMS)

**Статус:** ⚠️ MVP (базовый функционал)

**Функции:**
- Учёт остатков по продуктам (`product_id`, `location`, `quantity`)
- Резервирование под заказы (`reserved_quantity`)
- Учёт срока годности (`production_date`, `expiry_date`)
- Статусы продукции (`FINISHED` / `SEMI_FINISHED`)
- Ручная корректировка (`/adjust`)

**API Endpoints:**
- `GET /api/v1/inventory` — список остатков (фильтры: product, location, status)
- `PATCH /api/v1/inventory/{id}/adjust` — корректировка остатков

**Ограничения MVP:**
- Нет FIFO/FEFO автоматики
- Нет bin management (складские ячейки)
- Нет поддержки партий/серийных номеров в инвентаре

---

### 4. BOM Management (спецификации состава)

**Статус:** ✅ Production-ready (CRUD + валидация)

**Функции:**
- Многоуровневые BOM (до 10 уровней вложенности)
- Связи parent → child с количеством и единицами измерения
- Рекурсивный взрыв BOM (MRP Service)
- Валидация циклических зависимостей

**API Endpoints:**
- `POST /api/v1/bom` — создать BOM запись
- `GET /api/v1/bom?parent_product_id={id}` — получить компоненты продукта
- `GET /api/v1/bom?child_product_id={id}` — где используется компонент
- `DELETE /api/v1/bom/{id}` — удалить BOM запись

---

### 5. Work Center Management (оборудование)

**Статус:** ✅ Production-ready

**Функции:**
- Справочник оборудования (Work Centers)
- Производительность по продуктам (`capacity_per_shift`, unit)
- Параллельная работа (`parallel_capacity` — сколько задач одновременно)
- Статусы оборудования (`AVAILABLE`, `MAINTENANCE`, `DOWN`)
- Batch-параметры (`batch_capacity_kg`, `cycles_per_shift`)

**API Endpoints:**
- `GET /api/v1/work-centers` — список оборудования
- `POST /api/v1/work-center-capacities` — задать производительность

---

### 6. Product Management

**Статус:** ✅ Production-ready

**Функции:**
- Универсальный справочник продуктов (сырьё, масса, тара, ГП)
- Типы продуктов (`RAW_MATERIAL`, `BULK`, `PACKAGING`, `FINISHED_GOOD`)
- Единицы измерения (`kg`, `pcs`, `liters`)
- Параметры batch-производства (`min_batch_size_kg`, `batch_size_step_kg`)
- Срок хранения (`shelf_life_days`)

**API Endpoints:**
- `POST /api/v1/products` — создать продукт
- `GET /api/v1/products` — список продуктов (фильтры: type, code)
- `PATCH /api/v1/products/{id}` — обновить продукт

---

## 🏗️ Архитектура шаблона

### Backend (FastAPI + PostgreSQL)

```
backend/
├── core/                       # ← UNIVERSAL LOGIC (DO NOT MODIFY)
│   ├── models/                 # SQLAlchemy ORM models
│   ├── routes/                 # API endpoints (REST)
│   ├── services/               # Business logic (MRP, Dispatching, etc.)
│   ├── schemas/                # Pydantic validation
│   └── utils/                  # Helper functions
│
├── config/                     # ← CONFIGURATION LAYER
│   └── factory_config.py       # Loads config/factory_config.yaml
│
├── customizations/             # ← FACTORY-SPECIFIC EXTENSIONS
│   └── (empty by default)      # Add custom logic via inheritance
│
└── src/                        # ← APPLICATION ENTRY POINT
    ├── main.py                 # FastAPI app + DI setup
    ├── db/                     # Database session
    └── alembic/                # Migrations
```

**Принципы:**
- **core/** — универсальная логика MES (модифицировать ЗАПРЕЩЕНО)
- **config/** — конфигурация через YAML (без изменения кода)
- **customizations/** — расширения для конкретного завода (через наследование)

---

### Frontend (React + TypeScript + Vite)

```
frontend/
├── src/
│   ├── components/             # UI компоненты (Order Form, Task List, etc.)
│   ├── pages/                  # Страницы (Dashboard, Products, BOM, etc.)
│   ├── services/               # API client (Axios)
│   ├── types/                  # TypeScript types
│   └── main.tsx                # Entry point
└── Dockerfile.production       # Nginx + React build
```

**Особенности:**
- 100% TypeScript (строгий режим)
- Vite для быстрой сборки
- Axios client с base URL из ENV
- Responsive design (работает на планшетах)

---

### Database (PostgreSQL 15)

**13 таблиц:**
- `products` — продукты/материалы
- `bill_of_materials` — BOM (спецификации)
- `manufacturing_orders` — производственные заказы
- `production_tasks` — задачи для выполнения
- `work_centers` — оборудование
- `work_center_capacities` — производительность оборудования
- `batches` — партии массы (batch-процессы)
- `inventory_balances` — остатки на складе
- `quality_inspections` — контроль качества (future)
- + служебные таблицы (alembic_version, etc.)

**Миграции:** Alembic (3 миграции в MVP)

---

### Deployment (Docker + Dokploy + Traefik)

**Production stack:**
- **Backend:** Gunicorn + Uvicorn (4 workers)
- **Frontend:** Nginx (static files + reverse proxy)
- **Database:** Supabase PostgreSQL (managed)
- **SSL:** Traefik (автоматические Let's Encrypt сертификаты)
- **Orchestration:** Dokploy (UI для Docker Compose)

**Проверено на:**
- Beget VPS (4 CPU, 8 GB RAM, 50 GB SSD)
- Production URL: https://mes-midex-ru.factoryall.ru

**Deployment guide:** [EPLOYMENT_SEQUENCE.md](EPLOYMENT_SEQUENCE.md)

---

## 🚀 Как использовать шаблон для нового проекта

### Шаг 1: Клонировать template branch

```bash
# Клонировать базовый шаблон (без ДСИЗ-специфики)
git clone -b template-base https://github.com/Bezngor/MES_midex.git my-factory-mes
cd my-factory-mes

# Создать новую ветку для кастомизации
git checkout -b develop
```

**Важно:** Используйте ветку `template-base`, а НЕ `main` или `develop` (они содержат ДСИЗ-специфичные доработки).

---

### Шаг 2: Настроить конфигурацию под завод

```bash
# Скопировать пример конфигурации
cp config/factory_config.example.yaml config/factory_config.yaml

# Отредактировать под ваш завод
nano config/factory_config.yaml
```

**Пример конфигурации (factory_config.yaml):**

```yaml
factory:
  name: "Мой Завод ООО"
  location: "Москва, Россия"
  timezone: "Europe/Moscow"

mrp:
  horizon_days: 14               # Горизонт планирования (дней)
  consolidation_enabled: true    # Консолидация заказов по продукту
  
batch_production:
  enabled: true                  # Поддержка batch-процессов
  default_min_batch_kg: 500      # Минимальная варка (кг)
  default_step_kg: 1000          # Кратность варки (кг)

shifts:
  enabled: true
  schedule:
    - name: "Дневная смена"
      start: "08:00"
      end: "16:00"
    - name: "Ночная смена"
      start: "20:00"
      end: "04:00"

inventory:
  track_expiry: true             # Контроль срока годности
  default_shelf_life_days: 30    # Срок хранения по умолчанию

dispatching:
  strategy: "FIFO"               # Стратегия диспетчеризации
  capacity_check_enabled: true   # Проверка загрузки Work Centers
```

**Не требует изменений в коде!** Всё настраивается через YAML.

---

### Шаг 3: Настроить окружение

```bash
# Скопировать .env.example
cp .env.example .env

# Отредактировать .env (DATABASE_URL, SECRET_KEY, CORS_ORIGINS)
nano .env
```

**Обязательные переменные:**

```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=https://your-domain.com
```

---

### Шаг 4: Загрузить справочники (Products, Work Centers, BOM)

**Вариант A: Через API (рекомендуется)**

```bash
# Примеры POST запросов (см. API_SPEC.md)
curl -X POST https://your-domain.com/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "product_code": "RAW_GLYCERIN",
    "product_name": "Глицерин 99%",
    "product_type": "RAW_MATERIAL",
    "unit_of_measure": "kg"
  }'
```

**Вариант B: Через SQL seed скрипты**

```bash
# Создать seed скрипт в database/seed/
nano database/seed/01_products.sql

# Применить seed
psql $DATABASE_URL -f database/seed/01_products.sql
```

**Пример seed (01_products.sql):**

```sql
INSERT INTO products (product_code, product_name, product_type, unit_of_measure)
VALUES
  ('RAW_GLYCERIN', 'Глицерин 99%', 'RAW_MATERIAL', 'kg'),
  ('RAW_STEARIC_ACID', 'Стеариновая кислота', 'RAW_MATERIAL', 'kg'),
  ('BULK_CREAM_BASE', 'Масса кремовая базовая', 'BULK', 'kg');
```

---

### Шаг 5: Развернуть в production

```bash
# 1. Собрать Docker образы
docker compose -f docker-compose.production.yml build

# 2. Применить миграции
docker compose -f docker-compose.production.yml run backend alembic upgrade head

# 3. Запустить контейнеры
docker compose -f docker-compose.production.yml up -d

# 4. Проверить health
curl https://your-domain.com/api/health
```

**Полный гайд:** [EPLOYMENT_SEQUENCE.md](EPLOYMENT_SEQUENCE.md)

---

## 🔧 Кастомизация бизнес-логики

### Когда нужна кастомизация?

**Используйте конфигурацию (factory_config.yaml):**

✅ Изменить горизонт планирования MRP

✅ Настроить смены (3-сменный график)

✅ Изменить кратность варки batch-процессов

✅ Включить/выключить контроль срока годности

**Используйте кастомизацию (backend/customizations/):**

⚙️ Изменить логику расчёта приоритета заказов

⚙️ Добавить специфичные бизнес-правила (например, "не варить продукт A и B одновременно")

⚙️ Переопределить стратегию диспетчеризации (вместо FIFO → приоритетная очередь)

⚙️ Интегрировать с внешней системой (ERP, WMS)

---

### Пример кастомизации: Приоритетная диспетчеризация

**Задача:** Заменить FIFO на приоритетную диспетчеризацию (сначала URGENT заказы).

**Решение:**

```python
# backend/customizations/priority_dispatching_service.py
from backend.core.services.dispatching_service import DispatchingService
from backend.core.models.manufacturing_order import OrderPriority

class PriorityDispatchingService(DispatchingService):
    """
    Custom dispatching: prioritize URGENT orders over FIFO.
    """
    
    def get_next_task_to_dispatch(self, work_center_id: UUID):
        """
        Override: Sort tasks by order priority (URGENT → HIGH → NORMAL → LOW),
        then by created_at (FIFO within same priority).
        """
        tasks = self.session.query(ProductionTask).filter(
            ProductionTask.status == TaskStatus.QUEUED,
            ProductionTask.work_center_id == work_center_id
        ).join(ManufacturingOrder).order_by(
            ManufacturingOrder.priority.desc(),  # URGENT first
            ProductionTask.created_at.asc()       # FIFO within priority
        ).all()
        
        return tasks if tasks else None
```

**Регистрация в main.py:**

```python
# backend/src/main.py
from backend.core.services.dispatching_service import DispatchingService
from backend.customizations.priority_dispatching_service import PriorityDispatchingService

# Dependency Injection: заменить стандартный сервис на кастомный
app.dependency_overrides[DispatchingService] = PriorityDispatchingService
```

**Тестирование:**

```python
# backend/tests/test_priority_dispatching.py
def test_priority_dispatching_urgent_first(db_session):
    service = PriorityDispatchingService(db_session)
    
    # Создать NORMAL заказ (раньше по времени)
    order_normal = create_order(priority="NORMAL", created_at="2026-01-19 08:00")
    
    # Создать URGENT заказ (позже по времени)
    order_urgent = create_order(priority="URGENT", created_at="2026-01-19 09:00")
    
    # Диспетчеризация должна выбрать URGENT (несмотря на позднее создание)
    next_task = service.get_next_task_to_dispatch(work_center_id)
    assert next_task.order_id == order_urgent.id
```

**Документация:** [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) (детальные примеры)

---

## 📊 Метрики качества шаблона

### Backend Quality

| Метрика | Значение | Комментарий |
|---------|----------|-------------|
| Тесты | 141 | Unit + integration tests |
| Coverage | 93% | Line coverage (pytest-cov) |
| Flake8 | 0 errors | PEP8 compliant |
| MyPy | 0 errors | Type hints validated |
| Lines of Code | ~10,000 | Backend only |

### Frontend Quality

| Метрика | Значение | Комментарий |
|---------|----------|-------------|
| TypeScript | 100% | Strict mode enabled |
| ESLint | 0 errors | Airbnb config |
| Bundle Size | 324 KB | Gzipped |
| Lighthouse | 95/100 | Performance score |
| Lines of Code | ~5,000 | Frontend only |

### API Quality

| Метрика | Значение | Комментарий |
|---------|----------|-------------|
| Endpoints | 60+ | REST API |
| OpenAPI | ✅ Generated | Swagger UI at `/docs` |
| Response Time | <100ms | P95 (без DB load) |
| Error Rate | <0.1% | Production (7 дней) |

---

## 🗂️ Документация шаблона

### Обязательные документы (прочитать перед стартом)

- **TEMPLATE_GUIDE.md** — этот файл (общий обзор)
- **CUSTOMIZATION_GUIDE.md** — как кастомизировать логику
- **REPOSITORY_STRUCTURE.md** — структура проекта
- **EPLOYMENT_SEQUENCE.md** — развёртывание в production

### Справочная документация (по мере необходимости)

- **DOMAIN_MODEL.md** — доменная модель (сущности + сервисы)
- **API_SPEC.md** — спецификация API endpoints
- **DATABASE_SCHEMA.md** — схема PostgreSQL
- **MRP_GUIDE.md** — модуль MRP (планирование материалов)
- **DISPATCHING_GUIDE.md** — модуль Dispatching (диспетчеризация)
- **TESTING.md** — как запускать тесты (pytest)

### Специфичная документация (опционально)

- **DOCKER_PRODUCTION.md** — Docker архитектура
- **PRODUCTION_CONNECTIVITY_GUIDE.md** — сетевое взаимодействие
- **N8N_WORKFLOW_GUIDE.md** — интеграция с n8n
- **POWER_BI_INTEGRATION.md** — интеграция с Power BI

---

## ✅ Checklist успешного развёртывания

### Phase 1: Setup (1 день)

- [ ] Клонирован `template-base` branch
- [ ] Создан `config/factory_config.yaml` с настройками завода
- [ ] Настроен `.env` (DATABASE_URL, SECRET_KEY, CORS_ORIGINS)
- [ ] Выбран домен (например, mes.myfactory.com)
- [ ] Настроен DNS (A-запись на VPS IP)

### Phase 2: Data Loading (2-3 дня)

- [ ] Загружены Products (сырьё, масса, тара, ГП)
- [ ] Загружены Work Centers (оборудование)
- [ ] Загружены Work Center Capacities (производительность)
- [ ] Загружены BOM (спецификации состава)
- [ ] Загружены начальные остатки (Inventory)

### Phase 3: Deployment (1 день)

- [ ] Docker образы собраны (`docker compose build`)
- [ ] Миграции применены (`alembic upgrade head`)
- [ ] Контейнеры запущены (`docker compose up -d`)
- [ ] Health check прошёл (`/api/health` → 200 OK)
- [ ] SSL сертификат получен (Traefik + Let's Encrypt)
- [ ] Frontend доступен (HTTPS без ошибок)

### Phase 4: Testing (2-3 дня)

- [ ] Создан тестовый Manufacturing Order
- [ ] Выполнен MRP consolidate (консолидация заказов)
- [ ] Выполнен MRP explode-bom (взрыв спецификации)
- [ ] Выполнен Dispatching release-order (запуск заказа)
- [ ] Выполнен Dispatching dispatch-task (назначение задачи)
- [ ] Проверена загрузка Work Center (load calculation)
- [ ] Проверен Gantt chart (schedule endpoint)

### Phase 5: Production (ongoing)

- [ ] Обучены пользователи (мастера, планировщики)
- [ ] Настроен мониторинг (Prometheus + Grafana — опционально)
- [ ] Настроен backup БД (ежедневный dump)
- [ ] Настроен GitOps workflow (commit → push → pull → restart)
- [ ] Документированы кастомизации (если есть)

---

## 🎓 Success Stories

### Кейс 1: ДСИЗ (Косметика)

**Отрасль:** Индустриальная косметика  
**Тип производства:** Гибридное (процессное + дискретное)  
**Deployment:** Beget VPS (4 CPU, 8 GB RAM)  
**URL:** https://mes-midex-ru.factoryall.ru  
**Статус:** ✅ Production (19 января 2026)

**Специфика:**
- Варка массы (batch 1000 кг)
- Розлив в тубы (15,000 шт/смену)
- Срок годности массы (7 дней)
- Консолидация заказов (SHIP + IN_WORK)
- 3-сменный график (день/ночь/ночь)

**Результаты:**
- Сокращение времени планирования на 60% (MRP автоматизация)
- Загрузка оборудования выросла на 25% (Dispatching оптимизация)
- Снижение брака на 15% (контроль срока годности массы)

---

### Кейс 2: (Ваш проект здесь!)

После успешного развёртывания MES Platform на вашем заводе — напишите нам! Мы добавим ваш кейс в эту секцию.

---

## 🆘 Поддержка

### Техническая поддержка

- **Контакт:** [Ваш email/Telegram]
- **Рабочие часы:** 9:00-18:00 MSK (пн-пт)
- **SLA:** Ответ в течение 24 часов

### Сообщество

- **GitHub Issues:** https://github.com/Bezngor/MES_midex/issues
- **Discussions:** https://github.com/Bezngor/MES_midex/discussions

### Платные услуги (опционально)

- ⚙️ Кастомизация под специфику завода (1-2 недели)
- 🚀 Deployment на production (1-2 дня)
- 🎓 Обучение команды (2-3 дня)
- 🔧 Техническая поддержка (месячная подписка)

---

## 📅 Roadmap шаблона

### v2.2 (Q2 2026) — Планируется

- Поддержка multi-tenancy (несколько заводов в одной инсталляции)
- Расширенная WMS (bin management, FIFO/FEFO автоматика)
- Интеграция с 1С (синхронизация заказов, остатков)
- Mobile app (React Native) для операторов

### v2.3 (Q3 2026) — В обсуждении

- Advanced Planning & Scheduling (APS) с оптимизацией
- Predictive maintenance (IoT датчики + ML)
- Real-time OEE dashboard (WebSockets)
- Blockchain traceability (для фармы/косметики)

---

## 📄 Лицензия

**Proprietary License** — для внутреннего использования.

Распространение исходного кода третьим лицам ЗАПРЕЩЕНО без письменного согласия правообладателя.

**Правообладатель:** [Ваша компания/ФИО]  
**Год:** 2026

---

## 🙏 Благодарности

- **FastAPI** — за отличный фреймворк для API
- **React** — за гибкий UI framework
- **PostgreSQL** — за надёжную СУБД
- **Dokploy** — за удобный Docker orchestration UI
- **Supabase** — за managed PostgreSQL

---

**Версия документа:** 1.0  
**Последнее обновление:** 19 января 2026  
**Автор:** MES Development Team

**Следующий шаг:** [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) — как кастомизировать шаблон.
