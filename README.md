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