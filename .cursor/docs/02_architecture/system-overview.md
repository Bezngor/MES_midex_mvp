# System Overview - MES_midex

## High-Level Architecture


┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Backend       │────▶│   PostgreSQL    │
│   React + TS    │     │   FastAPI       │     │   Database      │
│   Port: 5173    │◀────│   Port: 8000    │◀────│   Port: 5432    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
│                       │
▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   Docker        │     │   n8n           │
│   Compose       │     │   Workflows     │
└─────────────────┘     └─────────────────┘


## Backend Architecture

### Service Layers


┌─────────────────────────────────────────┐
│           API Routes (FastAPI)          │
│  /dsiz/planning, /dsiz/dispatching    │
├─────────────────────────────────────────┤
│           Service Layer                 │
│  DSIZMRPService, DSIZDispatchingService │
├─────────────────────────────────────────┤
│           Repository Layer              │
│  SQLAlchemy Models, Database Access     │
├─────────────────────────────────────────┤
│           Database                      │
│  PostgreSQL 15                          │
└─────────────────────────────────────────┘


### Key Patterns

- **Dependency Injection:** FastAPI `Depends()` for all services
- **Async/Await:** All database operations are async
- **Repository Pattern:** Data access abstracted through services
- **Factory Pattern:** Service creation via dependency functions

## Frontend Architecture

### Component Structure


src/
├── components/         # Reusable UI components
├── pages/              # Route-level components
├── hooks/              # Custom React hooks
├── services/           # API client functions
├── store/              # Zustand state management
└── types/              # TypeScript type definitions


### State Management

- **Zustand:** Global state for auth, user preferences
- **React Query:** Server state, caching, mutations
- **Local state:** Component-level with useState/useReducer

## Database Architecture

### Core Models

- **Product:** Finished goods, raw materials
- **ManufacturingOrder:** Production orders
- **ManufacturingRoute:** Production sequences
- **WorkCenter:** Production resources
- **ProductionTask:** Individual operations

### DSIZ Customization Models

- **WorkforceRequirements:** Labor planning
- **BaseRates:** Standard times
- **WorkCenterMode:** Resource configurations
- **ChangeoverMatrix:** Setup times
- **ProductWorkCenterRouting:** Resource assignments

## API Design

### Authentication

- **JWT tokens:** Stateless authentication
- **Refresh tokens:** Long-lived sessions
- **Role-based access:** Admin, operator, viewer

### Endpoints Structure


/api/v1/
├── auth/               # Login, logout, refresh
├── products/           # Product management
├── orders/             # Manufacturing orders
├── routes/             # Production routes
├── tasks/              # Production tasks
└── dsiz/               # DSIZ customization
├── planning/       # MRP planning
└── dispatching/    # Production dispatching


## Deployment Architecture

### Docker Setup

- **Development:** docker-compose.yml (local)
- **Staging:** docker-compose.staging.yml
- **Production:** docker-compose.production.yml

### VPS Configuration

- **Host:** gldkosfhmj
- **Path:** /opt/mes-platform
- **Services:** PostgreSQL, Backend, Frontend

## Integration Points

### n8n Workflows

- **Data import:** CSV processing
- **Notifications:** Email, Telegram alerts
- **Reporting:** Scheduled reports

### External Systems

- **Power BI:** Analytics and dashboards
- **ERP systems:** Data exchange via API

---

## Development Workflow

### Phase 1 (Current): Q Analysis → Cursor Prompts

1. Q analyzes code via GitHub API

MES Midex PM Agent, [20.02.2026 11:40]
2. Q generates Cursor-ready prompts
3. Developer implements in Cursor IDE
4. Push to GitHub → Q performs automated PR review

### Code Standards

- **Type hints:** All functions typed
- **Docstrings:** Google style
- **Tests:** pytest, coverage >80%
- **Linting:** ruff, mypy

---

## Important Files

- **Backend config:** `backend/pyproject.toml`
- **Frontend config:** `frontend/package.json`
- **Docker config:** `docker-compose.yml`
- **Environment:** `.env.example`

---

*Last Updated: 2026-02-20*