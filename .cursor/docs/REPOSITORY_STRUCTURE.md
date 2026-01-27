# MES Platform — Repository Structure (v2.1)

**Обновлено:** 19 января 2026  
**Статус:** После template рефакторинга

Эта структура отражает организацию кода после рефакторинга в template-архитектуру (core + config + customizations).

---

## 📂 Корневая структура проекта

```
mes-platform/
├── backend/                    # Python FastAPI backend
├── frontend/                   # React frontend
├── config/                     # Factory-specific configurations
├── .cursor/
│   └── docs/                   # Documentation
├── n8n-workflows/              # Exported n8n workflows (JSON)
├── docker-compose.yml          # Development Docker setup
├── docker-compose.production.yml # Production Docker setup
├── .env.example                # Environment variables template
├── .gitignore
└── README.md
```

---

## 🔧 Backend Structure (FastAPI)

```
backend/
├── core/                       # ← UNIVERSAL LOGIC (DO NOT CUSTOMIZE)
│   ├── models/                 # Domain entities (SQLAlchemy ORM)
│   │   ├── manufacturing_order.py
│   │   ├── work_center.py
│   │   ├── production_task.py
│   │   ├── product.py
│   │   ├── batch.py
│   │   ├── inventory_balance.py
│   │   ├── bom.py
│   │   └── ...
│   ├── routes/                 # API endpoints (REST)
│   │   ├── orders.py           # Manufacturing Orders CRUD
│   │   ├── tasks.py            # Production Tasks CRUD
│   │   ├── work_centers.py     # Work Centers CRUD
│   │   ├── products.py         # Products, BOM CRUD
│   │   ├── mrp.py              # MRP endpoints
│   │   ├── dispatching.py      # Dispatching endpoints
│   │   └── ...
│   ├── services/               # Business logic
│   │   ├── mrp_service.py      # Material Requirements Planning
│   │   ├── dispatching_service.py # Task dispatching & scheduling
│   │   ├── order_service.py    # Order management
│   │   ├── task_service.py     # Task management
│   │   └── ...
│   ├── schemas/                # Pydantic validation schemas
│   │   ├── order_schemas.py
│   │   ├── task_schemas.py
│   │   ├── product_schemas.py
│   │   └── ...
│   └── utils/                  # Utility functions
│       ├── datetime_utils.py
│       └── ...
│
├── config/                     # ← CONFIGURATION LAYER
│   ├── __init__.py
│   ├── factory_config.py       # Configuration loader (Python)
│   └── README.md               # How to use configuration
│
├── customizations/             # ← FACTORY-SPECIFIC CUSTOMIZATIONS
│   ├── __init__.py
│   ├── README.md               # Customization guide
│   └── (empty - add custom logic here)
│
├── src/                        # ← MAIN APPLICATION
│   ├── db/                     # Database layer
│   │   ├── __init__.py
│   │   ├── session.py          # SQLAlchemy session
│   │   └── base.py             # Declarative base
│   ├── alembic/                # Database migrations
│   │   ├── versions/
│   │   │   ├── 20240101000000_initial_schema.py
│   │   │   ├── 20260114000001_add_process_manufacturing_models.py
│   │   │   └── 20260114000002_add_ship_in_work_to_orderstatus.py
│   │   ├── env.py
│   │   └── script.py.mako
│   └── main.py                 # FastAPI application entry point
│
├── tests/                      # Unit & integration tests
│   ├── test_mrp_service.py     # 48 tests, 95% coverage
│   ├── test_dispatching_service.py # 66 tests, 92% coverage
│   ├── test_order_service.py
│   └── ...
│
├── Dockerfile                  # Development Dockerfile
├── Dockerfile.production       # Production Dockerfile (multi-stage)
├── alembic.ini                 # Alembic configuration
├── pyproject.toml              # Poetry dependencies
└── pytest.ini                  # Pytest configuration
```

### Ключевые изменения после рефакторинга:

1. **`backend/core/`** — Универсальная логика MES (не кастомизируется напрямую)
   - Все импорты используют `backend.core.*` вместо `backend.src.*`
   - 58+ файлов обновлено

2. **`backend/config/`** — Конфигурационный слой
   - `factory_config.py` — загрузчик YAML конфигураций
   - Singleton pattern для глобальной конфигурации

3. **`backend/customizations/`** — Кастомизация под конкретный завод
   - Переопределение логики через наследование
   - Dependency injection в `main.py`

4. **`backend/src/`** — Точка входа и инфраструктура
   - `main.py` — FastAPI application
   - `db/` — Database session management
   - `alembic/` — Database migrations

---

## 🎨 Frontend Structure (React + TypeScript)

```
frontend/
├── src/
│   ├── components/             # UI components
│   │   ├── OrderForm.tsx
│   │   ├── OrderList.tsx
│   │   ├── TaskList.tsx
│   │   ├── WIPDashboard.tsx
│   │   └── ...
│   ├── pages/                  # Page components
│   │   ├── Dashboard.tsx
│   │   ├── ProductsPage.tsx
│   │   ├── BOMPage.tsx
│   │   └── ...
│   ├── services/               # API client
│   │   └── api.ts              # Axios client with base URL
│   ├── types/                  # TypeScript types
│   │   └── api.ts              # API response types
│   ├── hooks/                  # Custom React hooks
│   ├── styles/                 # CSS/Tailwind styles
│   ├── main.tsx                # Entry point
│   └── index.css               # Global styles
│
├── public/                     # Static assets
├── index.html                  # HTML template
├── vite.config.ts              # Vite configuration
├── package.json
├── tsconfig.json
├── Dockerfile                  # Development Dockerfile
└── Dockerfile.production       # Production Dockerfile (nginx)
```

---

## ⚙️ Configuration Directory

```
config/
├── factory_config.example.yaml # Template configuration
├── factory_config.yaml         # Active configuration (gitignored)
├── shifts.example.yaml         # Work shifts template
└── rules.example.yaml          # Business rules template
```

**Purpose:** Factory-specific settings (shifts, batch sizes, MRP horizon, etc.)

**Usage:** Backend loads config via `backend.config.factory_config.get_factory_config()`

---

## 📚 Documentation Directory

```
.cursor/docs/
├── DOMAIN_MODEL.md             # Domain entities & business logic
├── API_SPEC.md                 # REST API specification
├── DATABASE_SCHEMA.md          # PostgreSQL schema
├── ARCHITECTURE.md             # System architecture
├── EPLOYMENT_SEQUENCE.md       # Production deployment guide
├── PRODUCTION_CONNECTIVITY_GUIDE.md # Network & connectivity
├── DOCKER_PRODUCTION.md        # Docker architecture
├── MRP_GUIDE.md                # MRP module documentation
├── DISPATCHING_GUIDE.md        # Dispatching module documentation
├── TESTING.md                  # Testing guide (pytest)
├── TESTING_SUMMARY.md          # Template refactoring test report
├── N8N_WORKFLOW_GUIDE.md       # n8n workflows documentation
├── POWER_BI_INTEGRATION.md     # Power BI integration guide
├── CHANGELOG.md                # Release notes
└── REPOSITORY_STRUCTURE.md     # This file
```

---

## 🔄 n8n Workflows Directory

```
n8n-workflows/
├── manufacturing_order_intake.json # Order created webhook
├── task_dispatched.json            # Task dispatched webhook
├── task_completed.json             # Task completed webhook
└── README.md                       # n8n setup instructions
```

---

## 🐳 Docker Configuration

### Development

- **File:** `docker-compose.yml`
- **Services:** backend (port 8000), frontend (port 3000), postgres
- **Usage:** `docker compose up -d`

### Production

- **File:** `docker-compose.production.yml`
- **Services:** backend (Gunicorn + Uvicorn), frontend (nginx)
- **Networks:** `dokploy-network` (Traefik), `main-supabase-1kebyl` (PostgreSQL)
- **Deployment:** Beget VPS with Dokploy

---

## 🗂️ Key Files

| File | Purpose |
|------|---------|
| `.env.example` | Environment variables template (DATABASE_URL, SECRET_KEY, CORS_ORIGINS) |
| `.gitignore` | Excludes `config/factory_config.yaml`, `.env`, `__pycache__`, etc. |
| `alembic.ini` | Alembic migrations config (script_location = backend/src/alembic) |
| `pyproject.toml` | Python dependencies (Poetry) |
| `pytest.ini` | Pytest configuration (141 tests, 93% coverage) |
| `README.md` | Project overview and quick start |

---

## 📊 Metrics (as of Jan 19, 2026)

- **Backend:** 58+ files refactored, 141 tests (93% coverage)
- **Frontend:** 6 pages, 12 components, 100% TypeScript
- **Database:** 13 tables, 3 migrations
- **API:** 60+ endpoints (REST)
- **Lines of Code:** ~15,000 (backend + frontend)

---

## 🔗 Related Documentation

- **Template Guide:** See `docs/TEMPLATE_GUIDE.md` (future)
- **Customization Guide:** See `docs/CUSTOMIZATION_GUIDE.md` (future)
- **Deployment Guide:** See `docs/EPLOYMENT_SEQUENCE.md`
- **API Documentation:** See `docs/API_SPEC.md`

---

## Changelog

**v2.1 (2026-01-19):**
- Обновлена структура после template рефакторинга.
- Добавлены: `backend/core/`, `backend/config/`, `backend/customizations/`.
- Обновлена организация тестов (141 тестов, 93% coverage).

**v2.0 (2026-01-15):**
- Добавлены модули MRP, Dispatching, Process Manufacturing.
- Расширена структура документации.

**v1.0 (2026-01-13):**
- Начальная структура проекта.
