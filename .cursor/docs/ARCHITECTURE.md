# System Architecture

## Overview

The system is a SaaS MES platform for discrete manufacturing, built with:

- Backend: FastAPI + SQLAlchemy + PostgreSQL.
- Frontend: React + TypeScript.
- Orchestration: n8n for integration and automation.
- Analytics: Power BI (via API export endpoints).

## Layers

- **Presentation Layer (Frontend)**:
  - React components and pages for MES operators, planners, and supervisors.
  - Communicates with backend via JSON/HTTP.

- **Application Layer (Backend API)**:
  - FastAPI routes in `backend/src/routes/`.
  - Applies MES-specific rules, handles requests, validates input, returns responses.

- **Domain & Service Layer**:
  - MES domain models in `backend/src/models/`.
  - Business logic and orchestration in `backend/src/services/`.

- **Infrastructure Layer**:
  - DB session management and migrations in `backend/src/db/`.
  - Integrations with n8n, ERP, WMS, and other systems.

## Data Flow (High-Level)

1. ERP sends or a user creates a `ManufacturingOrder`.
2. Backend creates the order, loads route, and generates `ProductionTask` records.
3. n8n workflows are triggered to coordinate external systems and notifications.
4. Operators and machines update task statuses via UI or integrations.
5. `GenealogyRecord` and `QualityInspection` data is collected.
6. Analytics endpoints expose data for Power BI dashboards.

## Production Infrastructure

### Deployment Architecture

- **VPS**: Beget Ubuntu 22.04 (155.212.184.11)
- **Orchestration**: Dokploy (Docker-based PaaS)
- **Database**: Supabase PostgreSQL (supabase-db:5432)
- **Automation**: n8n (n8n-ru.factoryall.ru)
- **Domain**: mes-midex-ru.factoryall.ru
- **SSL**: Traefik (managed by Dokploy)

### Docker Network

- **External network**: `dokploy`
- **Services**: 
  - `mes_backend` (FastAPI + Gunicorn, port 8000)
  - `mes_frontend` (Nginx, port 3000)
- **Database**: `supabase-db` (shared PostgreSQL instance)
- **Communication**: Services communicate via Docker internal DNS

### Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Dokploy Network                       │
│                    (External: dokploy)                  │
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   Frontend   │────────▶│   Backend    │             │
│  │  (nginx)     │  API    │  (gunicorn)  │             │
│  │  Port: 3000  │  Proxy  │  Port: 8000  │             │
│  └──────────────┘         └──────┬───────┘             │
│                                   │                      │
│                                   │ DATABASE_URL         │
│                                   ▼                      │
│                          ┌──────────────┐               │
│                          │   Supabase   │               │
│                          │  PostgreSQL  │               │
│                          │  Port: 5432  │               │
│                          └──────────────┘               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Container Specifications

**Backend Container**:
- Base: Python 3.11-slim
- Server: Gunicorn with Uvicorn workers (4 workers)
- Health: `/api/v1/health` endpoint
- Resources: 512MB memory, 0.5 CPU limit

**Frontend Container**:
- Base: Nginx Alpine
- Build: Multi-stage (Node.js builder → Nginx runtime)
- Proxy: `/api/*` → `mes_backend:8000`
- Resources: 256MB memory, 0.25 CPU limit

### Security

- **Network Isolation**: Services communicate via Docker network
- **Non-root User**: Backend runs as `appuser` (UID 1000)
- **HTTPS**: Traefik handles SSL termination
- **CORS**: Restricted to production domain
- **Secrets**: Environment variables from `.env` (not committed)

### Scaling

- **Stateless Design**: Both frontend and backend are stateless
- **Horizontal Scaling**: Multiple instances behind load balancer
- **Database**: Connection pooling handles concurrent connections
- **CDN**: Frontend static files can be served from CDN

For detailed Docker production architecture, see [DOCKER_PRODUCTION.md](./DOCKER_PRODUCTION.md).
