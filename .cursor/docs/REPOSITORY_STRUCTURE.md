saas-mes-platform/
├── backend/                      # Python (FastAPI) или Node.js (NestJS)
│   ├── src/
│   │   ├── models/              # Domainnye entities (PostgreSQL models)
│   │   │   ├── manufacturing_order.py
│   │   │   ├── work_center.py
│   │   │   ├── production_task.py
│   │   │   ├── genealogy.py
│   │   │   └── ...
│   │   ├── routes/              # API endpoints (REST)
│   │   │   ├── orders.py
│   │   │   ├── tasks.py
│   │   │   ├── work_centers.py
│   │   │   └── ...
│   │   ├── services/            # Business logic
│   │   │   ├── scheduling_service.py      # APS logic
│   │   │   ├── dispatching_service.py     # Task assignment
│   │   │   ├── quality_service.py         # QC/QA
│   │   │   └── ...
│   │   ├── db/
│   │   │   ├── models.py        # ORM (SQLAlchemy)
│   │   │   ├── schemas.py       # Pydantic (validation)
│   │   │   └── migrations/      # Alembic
│   │   └── main.py
│   ├── tests/
│   ├── docker/
│   └── requirements.txt / package.json
│
├── frontend/                     # React / Vue
│   ├── src/
│   │   ├── components/          # UI components
│   │   │   ├── TaskDispatcher.jsx
│   │   │   ├── WIPTracker.jsx
│   │   │   ├── QualityForm.jsx
│   │   │   └── ...
│   │   ├── pages/
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API client (axios)
│   │   ├── stores/              # State (Zustand / Redux)
│   │   └── styles/
│   ├── public/
│   └── package.json
│
├── n8n-workflows/               # Exported workflows as JSON
│   ├── manufacturing_order_intake.json
│   ├── task_dispatch.json
│   ├── alert_handling.json
│   └── erp_sync.json
│
├── database/
│   ├── schemas/                 # SQL DDL
│   ├── migrations/              # Alembic scripts
│   └── seed/                    # Test data
│
├── docs/
│   ├── DOMAIN_MODEL.md          # ← Переверстка из Части 1!
│   ├── API_SPEC.md              # OpenAPI/Swagger
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SCHEMA.md
│   └── n8n_WORKFLOW_GUIDE.md
│
├── .cursorrules                 # ← КРИТИЧНО для Cursor!
├── docker-compose.yml
└── README.md
