# MES Platform Project Structure

mes-platform/
├── backend/ # FastAPI Python backend
│ ├── src/
│ │ ├── models/ # SQLAlchemy ORM models
│ │ │ ├── manufacturing_order.py
│ │ │ ├── work_center.py
│ │ │ ├── production_task.py
│ │ │ ├── product.py # v2.0
│ │ │ ├── bom.py # v2.0
│ │ │ ├── batch.py # v2.0
│ │ │ ├── inventory.py # v2.0
│ │ │ └── ...
│ │ ├── routes/ # API endpoints (REST)
│ │ │ ├── orders.py
│ │ │ ├── tasks.py
│ │ │ ├── work_centers.py
│ │ │ ├── products.py # v2.0
│ │ │ ├── bom.py # v2.0
│ │ │ ├── batches.py # v2.0
│ │ │ ├── mrp.py # v2.0
│ │ │ └── dispatching.py # v2.1.0
│ │ ├── services/ # Business logic
│ │ │ ├── mrp_service.py # v2.0 MRP logic
│ │ │ ├── dispatching_service.py # v2.1.0 Task dispatch
│ │ │ └── ...
│ │ ├── db/
│ │ │ ├── database.py # DB connection
│ │ │ ├── schemas.py # Pydantic schemas
│ │ │ └── models.py # ORM models
│ │ ├── core/
│ │ │ ├── config.py # Environment config
│ │ │ └── security.py # JWT auth
│ │ └── main.py # FastAPI app
│ ├── tests/ # Pytest test suite
│ │ ├── test_mrp_service.py
│ │ ├── test_dispatching_service.py
│ │ └── ...
│ ├── alembic/ # Database migrations
│ │ └── versions/
│ ├── Dockerfile # Development Docker image
│ ├── Dockerfile.production # Production optimized image
│ ├── alembic.ini
│ ├── pyproject.toml # Poetry dependencies
│ └── pytest.ini
│
├── frontend/ # React + Vite frontend
│ ├── src/
│ │ ├── components/ # Reusable UI components
│ │ │ ├── TaskDispatcher.jsx
│ │ │ ├── WIPTracker.jsx
│ │ │ ├── InventoryManager.jsx # v2.0
│ │ │ ├── MRPPlanner.jsx # v2.0
│ │ │ └── ...
│ │ ├── pages/ # Route pages
│ │ │ ├── OrdersPage.jsx
│ │ │ ├── ProductsPage.jsx # v2.0
│ │ │ ├── BatchesPage.jsx # v2.0
│ │ │ └── ...
│ │ ├── services/ # API client (axios)
│ │ │ └── api.js
│ │ ├── hooks/ # Custom React hooks
│ │ ├── stores/ # State management
│ │ └── App.jsx
│ ├── public/
│ ├── Dockerfile # Development Docker image
│ ├── Dockerfile.production # Production nginx image
│ ├── nginx.conf # Production nginx config
│ ├── package.json
│ └── vite.config.js
│
├── .cursor/
│ └── docs/ # Documentation for Cursor AI
│ ├── DOMAIN_MODEL.md
│ ├── API_SPEC.md
│ ├── ARCHITECTURE.md
│ ├── DATABASE_SCHEMA.md
│ ├── MRP_GUIDE.md
│ ├── DISPATCHING_GUIDE.md
│ ├── N8N_WORKFLOW_GUIDE.md
│ ├── TESTING.md
│ ├── DEPLOYMENT.md # v2.1.0 Production
│ ├── DOCKER_PRODUCTION.md # v2.1.0 Production
│ └── CHANGELOG.md
│
├── n8n-workflows/ # n8n automation workflows
│ ├── manufacturing_order_intake.json
│ ├── task_dispatch_notification.json
│ └── ...
│
├── docs/ # Public documentation
│ ├── DEPLOYMENT.md # Production deployment guide
│ ├── DOCKER_PRODUCTION.md # Docker architecture
│ ├── ARCHITECTURE.md # System architecture
│ └── ...
│
├── .env.example # Environment variables template
├── .env.staging # Staging environment config
├── .gitignore
├── docker-compose.yml # Development environment
├── docker-compose.production.yml # Production deployment
└── README.md


## Key Directories

### Backend (`backend/`)
- **src/models**: SQLAlchemy ORM models for database entities
- **src/routes**: FastAPI API endpoints organized by domain
- **src/services**: Business logic layer (MRP, Dispatching, etc.)
- **tests/**: Pytest test suite with 93%+ coverage

### Frontend (`frontend/`)
- **src/components**: Reusable React components
- **src/pages**: Page-level components for routing
- **src/services**: API client for backend communication

### Documentation (`.cursor/docs/`)
- Cursor AI context files for intelligent code generation
- Updated with each major feature release

### Production Files (v2.1.0)
- **Dockerfile.production**: Optimized multi-stage builds
- **docker-compose.production.yml**: Production orchestration
- **nginx.conf**: Frontend reverse proxy configuration
- **.env.example**: Environment variables template

## Changelog
- **v2.1.0**: Added production deployment files and documentation
- **v2.0.0**: Added MRP module, Product/BOM/Batch/Inventory models
- **v1.0.0**: Initial MVP with Manufacturing Orders, Work Centers, Tasks
