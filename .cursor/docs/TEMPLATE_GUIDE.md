# MES Platform Template Guide

This repository is a **template** for creating custom MES (Manufacturing Execution System) implementations.

## Quick Start

### 1. Create New Project from Template

**GitHub UI:**
1. Click "Use this template" button
2. Name your repository (e.g., `my-factory-mes`)
3. Clone locally

**Or via CLI:**
```bash
gh repo create my-factory-mes --template mes-platform-template --private
cd my-factory-mes
```

### 2. Configure Factory Settings

```bash
# Copy example configs
cp config/factory_config.example.yaml config/factory_config.yaml
cp config/shifts.example.yaml config/shifts.yaml

# Edit factory_config.yaml
nano config/factory_config.yaml
```

Update these fields:
- `factory.name` — Your factory name
- `factory.location` — City, Country
- `factory.timezone` — Your timezone
- `planning.mrp_horizon_days` — Planning horizon
- `planning.default_batch_size_kg` — Default batch size

### 3. Add Custom Business Logic (Optional)

See [CUSTOMIZATION_GUIDE.md](./CUSTOMIZATION_GUIDE.md) for detailed instructions.

Example: Override MRP batch rounding logic

```bash
# Create custom service
touch backend/customizations/custom_mrp_logic.py
```

### 4. Deploy to Production

```bash
# Update .env file
cp .env.example .env
nano .env  # Set DATABASE_URL, SECRET_KEY, etc.

# Deploy with Docker
docker compose -f docker-compose.production.yml up -d --build
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for full deployment guide.

***

## What's Included

### Backend (FastAPI + PostgreSQL)
- ✅ **60+ API endpoints** — Products, BOM, Batches, Inventory, MRP, Dispatching
- ✅ **MRP Engine** — Order consolidation, BOM explosion, batch rounding
- ✅ **Dispatching** — Task scheduling, work center load calculation
- ✅ **141 unit tests** — 93% coverage
- ✅ **Configuration-driven** — YAML-based settings

### Frontend (React + TypeScript)
- ✅ **6 pages** — Dashboard, Products, BOM, Batches, Inventory, Schedule
- ✅ **Responsive UI** — Tailwind CSS
- ✅ **Real-time updates** — Polling mechanism

### Infrastructure
- ✅ **Docker deployment** — Multi-container orchestration
- ✅ **SSL/HTTPS** — Automatic Let's Encrypt via Traefik
- ✅ **PostgreSQL** — Database with Alembic migrations
- ✅ **Health checks** — `/api/v1/health` endpoint

***

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   MES Platform                       │
├──────────────┬──────────────┬──────────────────────┤
│   Frontend   │   Backend    │      Database         │
│   (React)    │  (FastAPI)   │   (PostgreSQL)        │
├──────────────┴──────────────┴──────────────────────┤
│              Configuration Layer                     │
│  (factory_config.yaml, shifts.yaml, rules.yaml)     │
├──────────────────────────────────────────────────────┤
│              Customization Layer                     │
│    (custom_mrp_logic.py, custom_validation.py)      │
└──────────────────────────────────────────────────────┘
```

### Directory Structure

```
mes-platform-template/
├── backend/
│   ├── core/                    ← Universal logic (don't modify)
│   │   ├── models/              ← SQLAlchemy models
│   │   ├── services/            ← Business logic
│   │   ├── routes/              ← API endpoints
│   │   └── schemas/             ← Pydantic schemas
│   ├── config/                  ← Configuration loader
│   │   ├── __init__.py
│   │   └── factory_config.py
│   ├── customizations/          ← Factory-specific code
│   │   ├── __init__.py
│   │   └── README.md
│   └── tests/                   ← Unit tests
├── frontend/
│   ├── src/
│   │   ├── components/          ← React components
│   │   ├── pages/               ← Page layouts
│   │   └── services/            ← API client
├── config/                      ← YAML configurations
│   ├── factory_config.example.yaml
│   ├── shifts.example.yaml
│   └── rules.example.yaml
├── docs/                        ← Documentation
│   ├── TEMPLATE_GUIDE.md        ← This file
│   ├── CUSTOMIZATION_GUIDE.md
│   ├── DOMAIN_MODEL.md
│   ├── API_SPEC.md
│   └── DEPLOYMENT.md
├── docker-compose.production.yml
├── .env.example
└── README.md
```

***

## Customization Points

### 1. Configuration (YAML)
Edit `config/*.yaml` files to customize:
- Planning horizon, batch sizes
- Work shifts and holidays
- MRP rules, dispatching logic
- Feature flags (enable/disable modules)

### 2. Business Logic (Python)
Create files in `backend/customizations/`:
- `custom_mrp_logic.py` — Override MRP calculations
- `custom_validation.py` — Add custom validation rules
- `custom_dispatching.py` — Modify scheduling logic

### 3. Frontend (React)
Create components in `frontend/src/customizations/`:
- Custom dashboards
- Factory-specific reports
- Branded UI elements

### 4. Workflows (n8n)
Add workflows in `n8n-workflows/`:
- ERP integration
- Notifications (Telegram, Slack)
- Automated reports

***

## Version Tags

Template uses semantic versioning:

- `v2.1.0-template` — Current stable version
- `v2.x.x-template` — Major releases (breaking changes)
- `v2.1.x-template` — Minor releases (new features)
- `v2.1.0-template-patch-x` — Patches (bug fixes)

To update your project with template changes:

```bash
# Add template as remote
git remote add template https://github.com/your-org/mes-platform-template.git

# Fetch template updates
git fetch template

# Merge template changes (resolve conflicts manually)
git merge template/main --allow-unrelated-histories
```

***

## Next Steps

1. ✅ Configure factory settings (`config/*.yaml`)
2. ✅ Add customizations if needed (`backend/customizations/`)
3. ✅ Deploy to production (see `DEPLOYMENT.md`)
4. ✅ Train users on UI
5. ✅ Monitor production (logs, metrics)

For detailed customization instructions, see [CUSTOMIZATION_GUIDE.md](./CUSTOMIZATION_GUIDE.md).
