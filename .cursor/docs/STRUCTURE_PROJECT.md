# MES Platform — Полная структура проекта

**Версия:** 2.1.0  
**Дата:** 20 января 2026  
**Последнее обновление:** 21 января 2026 (обновлено)

---

## 📂 Корневая структура

```
MES_midex/
├── .cursor/                          # Cursor AI контекст и документация
│   ├── _olds/                        # Старые версии документации
│   │   ├── 040-mes-domain_v1.mdc
│   │   ├── API_SPEC_v1.md
│   │   ├── CHANGELOG_v1.md
│   │   ├── DATABASE_SCHEMA_v1.md
│   │   ├── DEPLOYMENT_LEGACY.md
│   │   ├── DOMAIN_MODEL_v1.md
│   │   ├── MES PLATFORM AGENT v1.1.md
│   │   ├── README_v1.md
│   │   ├── ИНСТРУКЦИЯ-ПРОМПТ ДЛЯ AI АГЕНТОВ — MES PLATFORM PROJECT v1.md
│   │   └── info/                     # Дополнительные материалы
│   │       ├── bom_test.csv
│   │       ├── bom_test.txt
│   │       ├── bom_test.xlsx
│   │       ├── DSIZ_CUSTOMIZATION_#1_Domain_Context.md
│   │       ├── DSIZ_CUSTOMIZATION_#2_Customization_Architecture.md
│   │       ├── DSIZ_CUSTOMIZATION_#3_Data Model_&_DB_Customization.md
│   │       ├── DSIZ_CUSTOMIZATION_#4_API_Specification.md
│   │       ├── DSIZ_CUSTOMIZATION_#5_Frontend_Customization.md
│   │       ├── DSIZ_CUSTOMIZATION_#6_Testing_&_Validation_Strategy.md
│   │       ├── DSIZ_CUSTOMIZATION_#7_Deployment_&_Rollout_Plan.md
│   │       ├── Описание производства (draft).txt
│   │       ├── Описание производства (real).txt
│   │       ├── Специф_группировка.xlsx
│   │       ├── Специф_плоская.xlsx
│   │       # (файлы без STRUCTURE_PROJECT.md)
│   ├── docs/                         # Актуальная документация
│   │   ├── API_SPEC.md
│   │   ├── ARCHITECTURE.md
│   │   ├── CHANGELOG.md
│   │   ├── CUSTOMIZATION_GUIDE.md
│   │   ├── DATABASE_SCHEMA.md
│   │   ├── DISPATCHING_GUIDE.md
│   │   ├── DOCKER_PRODUCTION.md
│   │   ├── DOMAIN_MODEL.md
│   │   ├── EPLOYMENT_SEQUENCE.md
│   │   ├── MRP_GUIDE.md
│   │   ├── N8N_WORKFLOW_GUIDE.md
│   │   ├── POWER_BI_INTEGRATION.md
│   │   ├── PRODUCTION_CONNECTIVITY_GUIDE.md
│   │   ├── REPOSITORY_STRUCTURE.md
│   │   ├── STRUCTURE_PROJECT.md        # Этот файл
│   │   ├── TEMPLATE_GUIDE.md
│   │   ├── TESTING_REPORT.md
│   │   ├── TESTING_SUMMARY.md
│   │   └── TESTING.md
│   └── rules/                        # Правила для Cursor AI
│       ├── 010-architecture-mes.mdc
│       ├── 020-backend-fastapi.mdc
│       ├── 030-frontend-react.mdc
│       ├── 040-mes-domain.mdc
│       └── 050-dsiz-customization.mdc
│
├── backend/                          # FastAPI Backend
│   ├── __init__.py
│   ├── alembic.ini                   # Конфигурация Alembic
│   ├── Dockerfile                     # Docker для разработки
│   ├── Dockerfile.production          # Docker для production
│   ├── pyproject.toml                 # Poetry зависимости
│   ├── pytest.ini                    # Конфигурация pytest
│   ├── test_refactoring.py            # Тест рефакторинга
│   │
│   ├── config/                        # Конфигурационный слой
│   │   ├── __init__.py
│   │   └── factory_config.py          # Загрузчик YAML конфигураций
│   │
│   ├── core/                          # Универсальная логика (НЕ изменять)
│   │   ├── models/                   # SQLAlchemy ORM модели
│   │   │   ├── __init__.py
│   │   │   ├── batch.py               # Модель Batch (партии)
│   │   │   ├── bill_of_material.py    # Модель BOM
│   │   │   ├── enums.py               # Перечисления (статусы, типы)
│   │   │   ├── genealogy_record.py    # Генеалогия производства
│   │   │   ├── inventory_balance.py   # Остатки на складе
│   │   │   ├── manufacturing_order.py # Производственные заказы
│   │   │   ├── manufacturing_route.py # Маршруты производства
│   │   │   ├── product.py             # Продукты/материалы
│   │   │   ├── production_task.py     # Производственные задачи
│   │   │   ├── quality_inspection.py  # Контроль качества
│   │   │   ├── route_operation.py     # Операции маршрута
│   │   │   ├── work_center_capacity.py # Производительность оборудования
│   │   │   └── work_center.py         # Рабочие центры
│   │   │
│   │   ├── routes/                    # API endpoints (REST)
│   │   │   ├── __init__.py
│   │   │   ├── batches.py             # Endpoints для партий
│   │   │   ├── bom.py                 # Endpoints для BOM
│   │   │   ├── dispatch.py            # Endpoints для диспетчеризации (legacy)
│   │   │   ├── dispatching.py         # Endpoints для диспетчеризации
│   │   │   ├── health.py              # Health check endpoint
│   │   │   ├── inventory.py           # Endpoints для инвентаря
│   │   │   ├── manufacturing_routes.py # Endpoints для маршрутов
│   │   │   ├── mrp.py                 # Endpoints для MRP
│   │   │   ├── operations.py          # Endpoints для операций
│   │   │   ├── orders.py              # Endpoints для заказов
│   │   │   ├── products.py            # Endpoints для продуктов
│   │   │   ├── tasks.py               # Endpoints для задач
│   │   │   ├── work_center_capacities.py # Endpoints для производительности
│   │   │   └── work_centers.py        # Endpoints для рабочих центров
│   │   │
│   │   ├── schemas/                   # Pydantic схемы валидации
│   │   │   ├── __init__.py
│   │   │   ├── batch.py
│   │   │   ├── bom.py
│   │   │   ├── dispatching.py
│   │   │   ├── genealogy_record.py
│   │   │   ├── inventory.py
│   │   │   ├── manufacturing_order.py
│   │   │   ├── manufacturing_route.py
│   │   │   ├── mrp.py
│   │   │   ├── product.py
│   │   │   ├── production_task.py
│   │   │   ├── quality_inspection.py
│   │   │   ├── route_operation.py
│   │   │   ├── work_center_capacity.py
│   │   │   └── work_center.py
│   │   │
│   │   └── services/                  # Бизнес-логика
│   │       ├── __init__.py
│   │       ├── dispatching_service.py # Сервис диспетчеризации
│   │       ├── mrp_service.py         # Сервис MRP
│   │       ├── operation_service.py   # Сервис операций
│   │       ├── order_service.py       # Сервис заказов
│   │       ├── route_service.py       # Сервис маршрутов
│   │       ├── task_service.py        # Сервис задач
│   │       └── work_center_service.py # Сервис рабочих центров
│   │
│   ├── customizations/                # Кастомизация под завод
│   │   ├── __init__.py
│   │   ├── README.md                  # Документация кастомизаций
│   │   └── dsiz/                      # DSIZ-специфичные кастомизации
│   │       ├── routes/                 # DSIZ-специфичные API endpoints
│   │       │   ├── __init__.py
│   │       │   └── dsiz_planning_routes.py # Endpoints для планирования DSIZ
│   │       ├── schemas/                # Pydantic схемы для DSIZ
│   │       │   ├── __init__.py
│   │       │   └── planning.py        # Схемы для планирования
│   │       └── services/               # DSIZ-специфичные сервисы
│   │           ├── __init__.py
│   │           ├── dsiz_mrp_service.py      # Кастомный MRP сервис для DSIZ
│   │           └── dsiz_workforce_service.py # Сервис управления персоналом
│   │
│   ├── src/                           # Точка входа приложения
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI приложение
│   │   ├── core/
│   │   │   └── __init__.py
│   │   └── db/                        # Работа с БД
│   │       ├── migrations/           # Alembic миграции
│   │       │   ├── __init__.py
│   │       │   ├── env.py             # Конфигурация Alembic
│   │       │   ├── script.py.mako     # Шаблон миграции
│   │       │   └── versions/         # Версии миграций
│   │       │       ├── .gitkeep
│   │       │       ├── 20240101000000_initial_schema.py
│   │       │       ├── 20260114000001_add_process_manufacturing_models.py
│   │       │       └── 20260114171052_add_ship_in_work_to_orderstatus.py
│   │       └── session.py             # SQLAlchemy session
│   │
│   └── tests/                         # Тесты (pytest)
│       ├── __init__.py
│       ├── conftest.py                 # Pytest фикстуры
│       ├── README.md
│       ├── test_api_integration.py
│       ├── test_order_service.py
│       ├── test_task_service.py
│       ├── api/                        # API тесты
│       │   ├── __init__.py
│       │   ├── test_batches_api.py
│       │   ├── test_bom_api.py
│       │   ├── test_dispatching_api.py
│       │   ├── test_inventory_api.py
│       │   ├── test_mrp_api.py
│       │   ├── test_products_api.py
│       │   └── test_work_center_capacities_api.py
│       ├── models/                     # Тесты моделей
│       │   ├── __init__.py
│       │   ├── test_batch.py
│       │   ├── test_bom.py
│       │   ├── test_inventory.py
│       │   ├── test_product.py
│       │   └── test_work_center_capacity.py
│       └── services/                   # Тесты сервисов
│           ├── __init__.py
│           ├── test_dispatching_service.py
│           └── test_mrp_service.py
│
├── frontend/                           # React Frontend
│   ├── .gitignore
│   ├── check-node.ps1                # Проверка Node.js
│   ├── Dockerfile                     # Docker для разработки
│   ├── Dockerfile.production          # Docker для production
│   ├── fix-path-cursor.ps1            # Исправление путей для Cursor
│   ├── index.html                     # HTML шаблон
│   ├── INSTALLATION.md                # Инструкция по установке
│   ├── nginx.conf                     # Конфигурация Nginx
│   ├── package-lock.json              # Зависимости (lock)
│   ├── package.json                   # Зависимости npm
│   ├── postcss.config.js              # PostCSS конфигурация
│   ├── README.md
│   ├── tailwind.config.js             # Tailwind CSS конфигурация
│   ├── tsconfig.json                  # TypeScript конфигурация
│   ├── tsconfig.node.json             # TypeScript для Node.js
│   ├── vite.config.ts                 # Vite конфигурация
│   │
│   └── src/                            # Исходный код
│       ├── App.tsx                     # Главный компонент
│       ├── index.css                   # Глобальные стили
│       ├── main.tsx                    # Точка входа
│       ├── vite-env.d.ts               # Типы Vite
│       │
│       ├── components/                 # React компоненты
│       │   ├── batches/                # Компоненты партий
│       │   │   ├── BatchCard.tsx
│       │   │   └── BatchList.tsx
│       │   ├── bom/                    # Компоненты BOM
│       │   │   ├── BOMEditor.tsx
│       │   │   └── BOMTree.tsx
│       │   ├── common/                 # Общие компоненты
│       │   │   ├── Button.tsx
│       │   │   ├── Error.tsx
│       │   │   ├── index.ts
│       │   │   ├── Loading.tsx
│       │   │   └── Modal.tsx
│       │   ├── inventory/              # Компоненты инвентаря
│       │   │   └── InventoryDashboard.tsx
│       │   ├── mrp/                    # Компоненты MRP
│       │   │   └── MRPDashboard.tsx
│       │   ├── products/               # Компоненты продуктов
│       │   │   ├── ProductForm.tsx
│       │   │   └── ProductList.tsx
│       │   ├── scheduling/             # Компоненты планирования
│       │   │   └── GanttChart.tsx
│       │   ├── OrderForm.tsx           # Форма заказа
│       │   ├── OrderList.tsx           # Список заказов
│       │   └── TaskList.tsx            # Список задач
│       │
│       ├── pages/                      # Страницы приложения
│       │   ├── BatchesPage.tsx         # Страница партий
│       │   ├── BOMPage.tsx             # Страница BOM
│       │   ├── Dashboard.tsx           # Главная страница
│       │   ├── InventoryPage.tsx      # Страница инвентаря
│       │   ├── MRPPage.tsx             # Страница MRP
│       │   ├── ProductsPage.tsx       # Страница продуктов
│       │   └── SchedulePage.tsx       # Страница расписания
│       │
│       ├── services/                   # API клиент
│       │   ├── api.ts                  # Axios клиент
│       │   └── types.ts                # Типы API
│       │
│       ├── store/                      # Zustand stores
│       │   ├── useBatchStore.ts
│       │   ├── useBOMStore.ts
│       │   ├── useInventoryStore.ts
│       │   ├── useMRPStore.ts
│       │   ├── useProductStore.ts
│       │   └── useScheduleStore.ts
│       │
│       └── types/                       # TypeScript типы
│           └── api.ts                  # Типы API ответов
│
├── config/                             # Конфигурация завода
│   ├── dsiz_config.yaml.example        # DSIZ-специфичная конфигурация
│   ├── factory_config.example.yaml    # Пример конфигурации
│   └── shifts.example.yaml             # Пример графика смен
│
├── .env                                # Переменные окружения (gitignored)
├── .env.example                        # Пример .env
├── .env.staging                        # Staging окружение
├── .gitignore                          # Git ignore правила
├── .template-config.yaml               # Метаданные шаблона
├── docker-compose.yml                  # Docker Compose для разработки
├── docker-compose.production.yml        # Docker Compose для production
├── docker-compose.staging.yml          # Docker Compose для staging
└── README.md                           # Главный README

```

---

## 📊 Статистика проекта

### Backend
- **Модели:** 13 файлов (SQLAlchemy ORM)
- **Routes:** 15 файлов (core) + кастомизации (DSIZ)
- **Schemas:** 13 файлов (core) + кастомизации (DSIZ)
- **Services:** 7 файлов (core) + кастомизации (DSIZ)
- **Тесты:** 141 тест, 93% coverage
- **Миграции:** 3 версии
- **Customizations:** DSIZ (routes, schemas, services)

### Frontend
- **Компоненты:** 25+ файлов (React + TypeScript)
- **Страницы:** 7 страниц
- **Stores:** 6 Zustand stores
- **TypeScript:** 100% покрытие

### Документация
- **Основные документы:** 18 файлов в `.cursor/docs/`
- **Правила Cursor:** 5 файлов в `.cursor/rules/`
- **Старые версии:** 10+ файлов в `.cursor/_olds/`

---

## 🔑 Ключевые файлы

### Конфигурация
- `config/factory_config.example.yaml` — настройки завода
- `config/dsiz_config.yaml.example` — DSIZ-специфичная конфигурация
- `config/shifts.example.yaml` — пример графика смен
- `.env.example` — переменные окружения
- `backend/alembic.ini` — конфигурация миграций
- `backend/pytest.ini` — конфигурация тестов

### Docker
- `docker-compose.yml` — разработка
- `docker-compose.production.yml` — production
- `docker-compose.staging.yml` — staging
- `backend/Dockerfile.production` — production образ backend
- `frontend/Dockerfile.production` — production образ frontend

### Документация
- `README.md` — главный README с инструкциями
- `.cursor/docs/TEMPLATE_GUIDE.md` — руководство по использованию шаблона
- `.cursor/docs/CUSTOMIZATION_GUIDE.md` — руководство по кастомизации
- `.cursor/docs/API_SPEC.md` — спецификация API
- `.cursor/docs/DOMAIN_MODEL.md` — доменная модель

---

## 📝 Примечания

### Gitignore
Следующие файлы/папки игнорируются Git:
- `__pycache__/`, `*.pyc` — Python кэш
- `.env`, `.env.local` — переменные окружения
- `config/factory_config.yaml` — конфигурация завода (используется `.example`)
- `.pytest_cache/`, `.coverage` — тестовые артефакты
- `node_modules/` — npm зависимости
- `.DS_Store`, `Thumbs.db` — системные файлы

### Структура после template рефакторинга
- `backend/core/` — универсальная логика (НЕ изменять)
- `backend/config/` — конфигурационный слой
- `backend/customizations/` — кастомизация под завод
  - `dsiz/` — DSIZ-специфичные кастомизации (пример)
- `backend/src/` — точка входа приложения

### Примеры кастомизаций
- **DSIZ Routes:** `backend/customizations/dsiz/routes/dsiz_planning_routes.py` — API endpoints для планирования DSIZ
- **DSIZ Schemas:** `backend/customizations/dsiz/schemas/planning.py` — Pydantic схемы для планирования
- **DSIZ MRP Service:** `backend/customizations/dsiz/services/dsiz_mrp_service.py` — кастомная логика MRP для DSIZ
- **DSIZ Workforce Service:** `backend/customizations/dsiz/services/dsiz_workforce_service.py` — управление персоналом
- **DSIZ Config:** `config/dsiz_config.yaml.example` — DSIZ-специфичная конфигурация

---

**Последнее обновление:** 21 января 2026 (обновлено)  
**Версия:** 2.1.0

---

## 🔄 Изменения в структуре

### DSIZ Customizations (v2.1.0)
- Добавлена директория `backend/customizations/dsiz/` для DSIZ-специфичных кастомизаций
- **Routes:** `dsiz/routes/dsiz_planning_routes.py` — API endpoints для планирования
- **Schemas:** `dsiz/schemas/planning.py` — Pydantic схемы для планирования
- **Services:** 
  - `dsiz/services/dsiz_mrp_service.py` — кастомный MRP сервис для DSIZ
  - `dsiz/services/dsiz_workforce_service.py` — сервис управления персоналом
- **Config:** `config/dsiz_config.yaml.example` — DSIZ-специфичная конфигурация