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

(Extend this document as architecture evolves.)
