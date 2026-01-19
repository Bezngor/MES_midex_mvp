# MES Platform Template v2.1.0 🏭

> **This is a template repository.** Use it to create custom MES implementations for your factory.

SaaS Manufacturing Execution System (MES) template for discrete and process manufacturing.

## Quick Start

See [docs/TEMPLATE_GUIDE.md](./docs/TEMPLATE_GUIDE.md) for detailed instructions.

### 1. Create Project from Template

Click "Use this template" button above or:

```bash
gh repo create my-factory-mes --template mes-platform-template
```

### 2. Configure

```bash
cp config/factory_config.example.yaml config/factory_config.yaml
nano config/factory_config.yaml  # Edit settings
```

### 3. Deploy

```bash
docker compose -f docker-compose.production.yml up -d --build
```

***

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2+-blue.svg)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)

## What's Included

- ✅ **60+ API endpoints** — Products, BOM, Batches, Inventory, MRP, Dispatching
- ✅ **React Dashboard** — 6 pages
- ✅ **Configuration-driven** — YAML-based customization
- ✅ **141 unit tests** — 93% coverage
- ✅ **Production-ready** — Docker + SSL

See [docs/TEMPLATE_GUIDE.md](./docs/TEMPLATE_GUIDE.md) for architecture and customization guide.

### Manufacturing Core (v1.0)
- ✅ Manufacturing Orders management
- ✅ Work Centers & capacity planning
- ✅ Production Tasks dispatching
- ✅ Real-time WIP tracking

### Material Requirements Planning (v2.0)
- ✅ BOM explosion & net requirements calculation
- ✅ Batch rounding for process manufacturing
- ✅ Multi-level BOM support
- ✅ Inventory management & transactions

### Dispatching & Scheduling (v2.1)
- ✅ Intelligent task dispatching
- ✅ Work center load calculation
- ✅ Order release planning
- ✅ Parallel capacity management

### Integration
- ✅ n8n workflow automation
- ✅ RESTful API (FastAPI)
- ✅ Power BI analytics connector
- ✅ Webhook notifications

## 📋 Tech Stack

- **Backend:** FastAPI + Python 3.11 + SQLAlchemy
- **Frontend:** React 18 + Vite + TailwindCSS
- **Database:** PostgreSQL 15+ (Supabase)
- **Automation:** n8n
- **Testing:** Pytest (93%+ coverage)
- **Deployment:** Docker + Dokploy PaaS

## 🚀 Production Deployment

See [DEPLOYMENT.md](./docs/DEPLOYMENT.md) for detailed production deployment instructions.

### Quick Start (Production)

```bash
# 1. Clone repository
git clone -b develop https://github.com/Bezngor/MES_midex.git
cd MES_midex

# 2. Configure environment
cp .env.example .env
nano .env  # Edit with production credentials

# 3. Build and deploy
docker-compose -f docker-compose.production.yml up -d --build

# 4. Run database migrations
docker exec mes_backend alembic upgrade head

# 5. Verify deployment
curl https://mes-midex-ru.factoryall.ru/api/v1/health
Production URLs
Frontend: https://mes-midex-ru.factoryall.ru

Backend API: https://mes-midex-ru.factoryall.ru/api/v1

API Docs: https://mes-midex-ru.factoryall.ru/api/v1/docs

---

## 🏭 Using as Template for Your Factory

This repository serves as a **universal MES template** for manufacturing enterprises (discrete, process, and hybrid production).

### ✨ Template Features

- ✅ **Production-ready** — deployed at https://mes-midex-ru.factoryall.ru
- ✅ **ISA-95 compliant** — follows MES industry standards
- ✅ **Highly tested** — 141 tests, 93% code coverage
- ✅ **Modular architecture** — core (universal) + config (settings) + customizations (factory-specific)
- ✅ **GitOps-ready** — Docker + Dokploy + Traefik deployment

### 🚀 Quick Start (New Factory)

#### 1. Clone template branch

```bash
# Clone the universal template (without factory-specific customizations)
git clone -b template-base https://github.com/Bezngor/MES_midex.git my-factory-mes
cd my-factory-mes

# Create your own development branch
git checkout -b develop
```

**Important:** Use `template-base` branch, NOT `main` or `develop` (they contain factory-specific code).

---

#### 2. Configure for your factory

```bash
# Copy configuration template
cp config/factory_config.example.yaml config/factory_config.yaml

# Edit with your factory settings
nano config/factory_config.yaml
```

**Example configuration:**

```yaml
factory:
  name: "My Factory LLC"
  location: "Moscow, Russia"
  timezone: "Europe/Moscow"

mrp:
  horizon_days: 14               # Planning horizon (days)
  consolidation_enabled: true    # Consolidate orders by product

batch_production:
  enabled: true                  # Support batch processes
  default_min_batch_kg: 500      # Minimum batch size (kg)
  default_step_kg: 1000          # Batch size step (kg)

dispatching:
  strategy: "FIFO"               # Dispatching strategy
  capacity_check_enabled: true   # Check work center capacity
```

---

#### 3. Setup environment

```bash
# Copy .env template
cp .env.example .env

# Edit database URL, secret key, CORS origins
nano .env
```

---

#### 4. Deploy to production

```bash
# Build Docker images
docker compose -f docker-compose.production.yml build

# Apply database migrations
docker compose -f docker-compose.production.yml run backend alembic upgrade head

# Start containers
docker compose -f docker-compose.production.yml up -d

# Check health
curl https://your-domain.com/api/health
```

---

### 📚 Documentation

- **[TEMPLATE_GUIDE.md](.cursor/docs/TEMPLATE_GUIDE.md)** — complete template usage guide
- **[CUSTOMIZATION_GUIDE.md](.cursor/docs/CUSTOMIZATION_GUIDE.md)** — how to customize business logic
- **[EPLOYMENT_SEQUENCE.md](.cursor/docs/EPLOYMENT_SEQUENCE.md)** — production deployment guide
- **[API_SPEC.md](.cursor/docs/API_SPEC.md)** — REST API specification
- **[DOMAIN_MODEL.md](.cursor/docs/DOMAIN_MODEL.md)** — domain entities & services

---

### 🏭 Supported Industries

- **Discrete Manufacturing** — machinery, electronics, furniture
- **Process Manufacturing** — cosmetics, chemicals, food & beverage
- **Hybrid Production** — batch + discrete operations

---

### 📦 Core Modules

| Module | Status | Coverage | Description |
|--------|--------|----------|-------------|
| MRP | ✅ Production | 95% | Material Requirements Planning |
| Dispatching | ✅ Production | 92% | Task scheduling & work center load |
| Inventory | ⚠️ MVP | 85% | Simplified WMS (balances, reservations) |
| BOM | ✅ Production | 90% | Multi-level Bill of Materials |
| Products | ✅ Production | 88% | Product master data |
| Work Centers | ✅ Production | 87% | Equipment & capacity management |

---

### 🎓 Success Stories

#### DSIZ (Cosmetics Factory)

- **Industry:** Industrial cosmetics
- **Production Type:** Hybrid (batch cooking + discrete filling)
- **Deployment:** Beget VPS (4 CPU, 8 GB RAM)
- **URL:** https://mes-midex-ru.factoryall.ru

**Results:**
- ⏱️ **60% reduction** in planning time (MRP automation)
- 📈 **25% increase** in equipment utilization (Dispatching optimization)
- 📉 **15% reduction** in defects (shelf life control)

---

### 🔧 Customization Options

MES Platform supports two levels of customization:

#### 1. Configuration (No Code Changes)

Edit `config/factory_config.yaml`:
- MRP planning horizon
- Batch production parameters
- Work shifts schedule
- Dispatching strategy

#### 2. Business Logic Extension

Create custom services in `backend/customizations/`:
- Override MRP/Dispatching logic via inheritance
- Add factory-specific business rules
- Integrate with external systems (ERP, WMS, IoT)

See: **[CUSTOMIZATION_GUIDE.md](.cursor/docs/CUSTOMIZATION_GUIDE.md)** for detailed examples.

---

### 🆘 Support

- **GitHub Issues:** https://github.com/Bezngor/MES_midex/issues
- **Discussions:** https://github.com/Bezngor/MES_midex/discussions
- **Email:** support@your-company.com

---

### 📄 License

**Proprietary License** — for internal use only.  
Distribution of source code to third parties is PROHIBITED without written consent.

---

🛠️ Development Setup
Prerequisites
Python 3.11+

Node.js 18+

PostgreSQL 15+

Docker & Docker Compose

Local Development
bash
# 1. Clone repository
git clone https://github.com/Bezngor/MES_midex.git
cd MES_midex

# 2. Start development environment
docker-compose up -d

# 3. Access services
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
Manual Setup (without Docker)
Backend
bash
cd backend
pip install poetry
poetry install
poetry run alembic upgrade head
poetry run uvicorn backend.src.main:app --reload
Frontend
bash
cd frontend
npm install
npm run dev
🧪 Testing
bash
cd backend
poetry run pytest
# or with coverage
poetry run pytest --cov=backend/src --cov-report=html
Test coverage: 93%+ (141 tests passing)

See TESTING.md for detailed testing guide.

📚 Documentation
Architecture & Design
System Architecture

Domain Model

Database Schema

API Specification

Modules
MRP Guide

Dispatching Guide

n8n Workflow Guide

Deployment & Operations
Production Deployment

Docker Production Architecture

Testing Guide

🗂️ Project Structure
text
mes-platform/
├── backend/              # FastAPI backend
│   ├── src/             # Source code
│   ├── tests/           # Pytest tests
│   ├── alembic/         # DB migrations
│   └── Dockerfile.production
├── frontend/            # React frontend
│   ├── src/            
│   ├── Dockerfile.production
│   └── nginx.conf
├── .cursor/docs/        # AI context docs
├── docs/                # Public documentation
├── docker-compose.yml              # Development
├── docker-compose.production.yml   # Production
└── .env.example
See REPOSITORY_STRUCTURE.md for detailed structure.

📊 API Endpoints
Manufacturing Orders
POST /api/v1/orders - Create manufacturing order

GET /api/v1/orders - List orders

GET /api/v1/orders/{id} - Get order details

PATCH /api/v1/orders/{id} - Update order status

MRP (Material Requirements Planning)
POST /api/v1/mrp/run - Run MRP calculation

GET /api/v1/batches - List production batches

GET /api/v1/inventory - Check inventory levels

Dispatching
POST /api/v1/dispatching/release-orders - Release orders for production

POST /api/v1/dispatching/dispatch-tasks - Dispatch tasks to work centers

GET /api/v1/dispatching/work-center-load - Get work center load

Full API documentation: http://localhost:8000/docs (Swagger UI)

🔐 Environment Variables
See .env.example for required environment variables:

DATABASE_URL - PostgreSQL connection string

SECRET_KEY - JWT secret key (generate with openssl rand -hex 32)

CORS_ORIGINS - Allowed origins for CORS

ENVIRONMENT - development or production

🤝 Contributing
Fork the repository

Create feature branch (git checkout -b feature/amazing-feature)

Commit changes (git commit -m 'Add amazing feature')

Push to branch (git push origin feature/amazing-feature)

Open Pull Request

📝 Changelog
See CHANGELOG.md for version history.

Latest Release: v2.1.0
✨ Added DispatchingService with order release and task dispatch

✨ Work center load calculation with parallel capacity

✨ Production deployment configuration (Docker, nginx, Dokploy)

📚 Complete deployment documentation

🧪 90%+ test coverage for dispatching module

📄 License
This project is proprietary software. All rights reserved.

👥 Authors
Bezngor - Initial work - GitHub

🙏 Acknowledgments
FastAPI framework

React ecosystem

n8n automation platform

Dokploy PaaS

Production URL: https://mes-midex-ru.factoryall.ru
API Docs: https://mes-midex-ru.factoryall.ru/api/v1/docs

text