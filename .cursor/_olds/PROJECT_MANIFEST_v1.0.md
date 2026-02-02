# 📋 MES PLATFORM PROJECT MANIFEST v1.0

**Last Updated:** 2026-01-28 16:32 MSK  
**Status:** Production Stable (v1.0.0-dsiz)  
**Purpose:** Single source of truth для состояния проекта

***

## 🎯 PROJECT IDENTITY

| Параметр | Значение |
|----------|----------|
| **Название** | MES Platform v2.1.0 (DSIZ Customization) |
| **Тип** | SaaS Manufacturing Execution System |
| **Домен** | Дискретное + Процессное производство (гибрид) |
| **Кейс** | DSIZ — дерматологические средства (кремы, пасты, мыло) |
| **Архитектура** | Multi-tenant SaaS с factory-specific кастомизацией |
| **Лицензия** | Proprietary (internal) |

***

## 🌐 PRODUCTION ENVIRONMENT

### URLs & Endpoints
```
Production:  https://mes-midex-ru.factoryall.ru
Health:      https://mes-midex-ru.factoryall.ru/api/v1/health
API Docs:    https://mes-midex-ru.factoryall.ru/docs
ReDoc:       https://mes-midex-ru.factoryall.ru/redoc
```

### Infrastructure
```
VPS:         155.212.184.11 (Beget.com)
OS:          Ubuntu 20.04 LTS
CPU:         4 cores
RAM:         8 GB
Docker:      24.0.7 + Docker Compose v2
Proxy:       Traefik (Dokploy)
Database:    PostgreSQL 13 (Supabase)
Cache:       Redis 7 (optional)
Monitoring:  n8n workflows (n8n.factoryall.ru)
```

### Current Production Version
```
Tag:         v1.0.0-dsiz
Branch:      main (7b08f38)
Release:     27.01.2026
Status:      ✅ Stable (Health: {"status":"healthy","version":"2.1.0"})
Config:      ✅ DSIZ (Dermatological Products) — Russia, Europe/Moscow
```

***

## 🗂️ REPOSITORY STRUCTURE

### GitHub
```
URL:         https://github.com/Bezngor/MES_midex
Owner:       Bezngor
Visibility:  Private
```

### Active Branches
| Ветка | Назначение | Защита | Текущий коммит |
|-------|-----------|--------|----------------|
| **main** | Production | 🔒 Protected | 7b08f38 (v1.0.0-dsiz + docs) |
| **develop** | Integration | 🔒 Protected | 46d5f3f (merged docs) |
| **template-base** | Universal template | 🔒 READ-ONLY | f08fd2b (v2.1.0-template) |
| **feat/dsiz-phase1-mrp** | Archive (Phase 1-3) | — | b912225 (можно удалить) |

### Tags
```
Production:
  v1.0.0-dsiz                   (27.01.2026) — DSIZ Phase 1+2+3 complete
  v1.0.0-dsiz-wip-2026-01-27    (27.01.2026) — WIP backup before reorganization

Template:
  v2.1.0-template               (19.01.2026) — Universal MES template
  v2.1.0-ui                     (19.01.2026) — Frontend baseline
  v2.1.0-staging                (19.01.2026) — Staging release

Backups:
  backup-develop-2026-01-27     — Safety backup
  backup-main-2026-01-27        — Safety backup
```

### Protected Branch Rules
```
main:
  - Merge only from release/* branches
  - Require PR approval
  - Require status checks (CI green)
  - No force push
  - No deletion

develop:
  - Merge only from feat/*, fix/*, release/* branches
  - Require PR approval
  - Require status checks (CI green)
  - No force push
  - No deletion

template-base:
  - READ-ONLY (no direct pushes)
  - Changes only via template-update process
```

***

## 🏗️ TECHNICAL STACK

### Backend
```
Framework:       FastAPI 0.104+
ORM:             SQLAlchemy 2.0+
Database:        PostgreSQL 13
Migrations:      Alembic
Validation:      Pydantic v2
Testing:         pytest + pytest-cov
Coverage:        93% global, 91% DSIZ
API Docs:        OpenAPI 3.0 (Swagger/ReDoc)
Auth:            JWT (Bearer tokens)
```

### Frontend
```
Framework:       React 18.2+
Language:        TypeScript 5.0+
Build:           Vite 5.0+
State:           React Query + Context API
UI:              Tailwind CSS 3+
Charts:          Recharts
Forms:           React Hook Form + Zod
Testing:         Jest + React Testing Library
```

### DevOps
```
Containerization: Docker + Docker Compose
CI/CD:           GitHub Actions (planned)
Deployment:      GitOps (manual pull + restart)
Logging:         Docker logs + n8n monitoring
Secrets:         .env files (gitignored)
Reverse Proxy:   Traefik (via Dokploy)
```

***

## 📊 PROJECT METRICS (Current)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Test Coverage (Global)** | 93%+ | 93% | ✅ Met |
| **Test Coverage (DSIZ)** | 91%+ | 91% | ✅ Met |
| **Test Coverage (Core MRP/Disp)** | 95%+ | 95% | ✅ Met |
| **Red Tests** | 0 | 0 | ✅ Met |
| **API Endpoints** | 50+ | 60+ | ✅ Exceeded |
| **Database Tables** | 10+ | 13 | ✅ Exceeded |
| **Code in core/ (from DSIZ)** | 0% | 0% | ✅ Met |
| **Config in YAML** | 100% | 100% | ✅ Met |
| **GitOps Compliance** | 100% | 100% | ✅ Met |
| **Documentation Complete** | 100% | 98% | ⚠️ Near (2 files WIP) |

***

## 🎯 DEVELOPMENT PHASES

### ✅ Phase 1: Template Creation (19-23.01.2026)
**Status:** Complete  
**Tag:** v2.1.0-template  
**Deliverables:**
- Universal MES template (backend/core/)
- TEMPLATE_GUIDE.md, CUSTOMIZATION_GUIDE.md
- React dashboard baseline
- PostgreSQL schema (10 tables)
- 93% test coverage
- Docker production setup

### ✅ Phase 2: DSIZ Backend + API (23-26.01.2026)
**Status:** Complete  
**Tag:** v1.0.0-dsiz  
**Deliverables:**
- DSIZ-specific models (7 tables)
- Custom MRP service (batch conflicts, consolidation)
- Workforce planning logic
- QR labeling module (85% done)
- Alembic migrations
- DSIZ test suite (91% coverage)
- API endpoints (/dsiz/mrp, /dsiz/planning)
- DSIZ_CUSTOMIZATION_#1-7.md specs

### ✅ Phase 3: DSIZ Frontend (26-27.01.2026)
**Status:** Complete  
**Tag:** v1.0.0-dsiz  
**Deliverables:**
- Planning UI (/dsiz/planning)
- Shift actualization (/dsiz/shift)
- Master data admin (/dsiz/admin)
- React components (BatchCard, WorkforcePanel)
- TypeScript integration
- Jest + RTL tests (green)

### 📋 Phase 4: Advanced Features (28.01 - 03.02.2026)
**Status:** Planned  
**ETA:** v1.2.0-dsiz (30.01.2026)  
**Scope:**
- Drag & drop Gantt chart
- Real-time notifications (WebSocket)
- Advanced dispatching (priority-based)
- ERP integration (1C/SAP sync)
- Performance monitoring (OEE dashboards)
- Mobile-responsive UI

### 📋 Phase 5: Production Hardening (04-10.02.2026)
**Status:** Planned  
**ETA:** v1.5.0-dsiz (10.02.2026)  
**Scope:**
- GitHub Actions CI/CD
- Automated backups
- Monitoring & alerting (Prometheus/Grafana)
- Load testing (Locust)
- Security audit (OWASP)
- Performance optimization

***

## 🗃️ DATABASE SCHEMA

### Core Tables (Universal, 10 tables)
```
products                   — SKU каталог
bill_of_materials          — BOM иерархия
manufacturing_orders       — производственные заказы
batches                    — партии (process mfg)
work_centers               — рабочие центры (станки)
production_tasks           — задачи на операции
inventory_balances         — остатки сырья/ГП
inventory_transactions     — движения склада
shifts                     — смены
users                      — пользователи
```

### DSIZ Tables (Customization, 7 tables)
```
work_center_modes          — режимы РЦ (REACTOR/AUTO/MANUAL)
changeover_matrix          — матрица переналадок (batch conflicts)
base_rates                 — базовые нормы (кг/час, чел/опер)
workforce_requirements     — нормы персонала (по РЦ + роли)
labeling_rules             — правила маркировки (QR/без QR)
qr_availability            — наличие QR-меток на складе
product_routing            — технологические маршруты
```

### Migrations
```
Latest:  20260125_dsiz_phase2_tables (27.01.2026)
Status:  ✅ Applied to production
Tool:    Alembic (auto-generate + manual edits)
```

***

## 📚 DOCUMENTATION INDEX

### Core Documentation (✅ Complete)
| Файл | Версия | Описание |
|------|--------|----------|
| `README.md` | v2.1.0 | Project overview |
| `MES_RULES.md` | v2.0 | 5 основных правил (27.01) |
| `GIT_WORKFLOW.md` | v1.1 | Git process, checklists (27.01) |
| `CUSTOMIZATION_GUIDE.md` | v2.1.0 | DI pattern, 4 сценария |
| `TEMPLATE_GUIDE.md` | v2.1 | Template usage |
| `REPOSITORY_STRUCTURE.md` | v2.1 | Directory navigation |
| `DOMAIN_MODEL.md` | v2.1 | Business logic (MRP/Disp) |
| `API_SPEC.md` | v2.1 | REST endpoints |
| `MASTER_PROMPT.md` | v1.0 | AI development rules (27.01) |
| `CONTEXT_STACK.md` | v1.0 | State machine (27.01) |

### DSIZ Specs (✅ Complete)
```
DSIZ_CUSTOMIZATION_#1.md  — Domain context (production processes)
DSIZ_CUSTOMIZATION_#2.md  — Architecture (DI setup)
DSIZ_CUSTOMIZATION_#3.md  — Data model & DB
DSIZ_CUSTOMIZATION_#4.md  — API specification
DSIZ_CUSTOMIZATION_#5.md  — Frontend customization
DSIZ_CUSTOMIZATION_#6.md  — Testing & validation
DSIZ_CUSTOMIZATION_#7.md  — Deployment & rollout
DSIZ_TEST_GENERATION_GUIDE.md — Test standards
DSIZ_DEPLOYMENT_LESSONS.md — Phase 2 lessons learned
```

### In Progress (🚧 50-80%)
```
DEPLOYMENT.md             — Production deployment (50% done)
ROLLBACK_PROCEDURES.md    — Emergency procedures (design phase)
```

### Planned (📋 Phase 4-5)
```
MONITORING.md             — Observability
TROUBLESHOOTING.md        — Common issues
PERFORMANCE_TUNING.md     — Optimization
SECURITY.md               — Security best practices
```

***

## ⚙️ CUSTOMIZATION ARCHITECTURE

### Pattern: Dependency Injection (DI)
```
✅ backend/core/              → Universal template (READ-ONLY)
✅ backend/customizations/dsiz/ → DSIZ-specific (inheritance + DI)
✅ config/factory_config.yaml → YAML config (not hardcoded)
❌ backend/core/ changes      → PROHIBITED
```

### Active Customizations
| Module | Status | Coverage | Location |
|--------|--------|----------|----------|
| **DSIZMRPService** | ✅ Complete | 94% | `customizations/dsiz/services/mrp_service.py` |
| **BatchConflictDetection** | ✅ Complete | 92% | `customizations/dsiz/services/batch_conflict_*.py` |
| **WorkforcePlanning** | ✅ Complete | 88% | `customizations/dsiz/services/workforce_*.py` |
| **QRLabeling** | 🚧 60% Done | 85% | `customizations/dsiz/services/qr_labeling.py` |
| **ERPIntegration (1C)** | 📋 Design Done | — | `customizations/dsiz/integrations/erp_*.py` |

***

## 🚨 CRITICAL RULES (NEVER VIOLATE!)

### Architecture Rules
```
❌ НЕ ИЗМЕНЯТЬ backend/core/
❌ НЕ ИЗМЕНЯТЬ template-base ветку
❌ НЕ КОММИТИТЬ .env, factory_config.yaml
❌ НЕ УДАЛЯТЬ ТЕСТЫ
❌ НЕ МЕНЯТЬ БД без Alembic миграции
❌ НЕ ДЕПЛОИТЬ с красными тестами
❌ НЕ ДЕПЛОИТЬ из feat/* (только из main!)
❌ НЕ git push --force в main/develop
```

### Git Workflow Rules
```
✅ Всегда работать в feat/* или fix/* ветках
✅ Pull Request обязательны (feat/* → develop)
✅ Release через release/* → main
✅ Тегировать production после каждого merge в main
✅ Использовать Conventional Commits (feat:, fix:, docs:, etc.)
✅ Деплой только из main (git pull + docker restart)
```

### Testing Rules
```
✅ Минимум 90% coverage для DSIZ модулей
✅ Минимум 93% global coverage
✅ 0 red tests перед commit
✅ Тесты для всей бизнес-логики (MRP, Dispatching)
✅ Pytest перед каждым push
```

***

## 🎯 ARCHITECTURAL DECISIONS (LOG)

### ✅ Decision 1: Dependency Injection for Customizations
**Date:** 2025-01-25  
**Rationale:** Avoid modifying `backend/core/`, maintain template integrity  
**Implementation:** `app.dependency_overrides[Service] = CustomService`  
**Document:**  CUSTOMIZATION_GUIDE.md [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_27c490ee-2624-4094-bd8d-c6940628e2ff/7d8f16ad-fea4-424d-af78-5a300b68b87b/CUSTOMIZATION_GUIDE.md)

### ✅ Decision 2: YAML Configuration (Not Hardcoded)
**Date:** 2025-01-25  
**Rationale:** Enable scalability across different factories  
**Implementation:** `config/factory_config.yaml`  
**Document:**  MES_RULES.md [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_27c490ee-2624-4094-bd8d-c6940628e2ff/7a38f3bb-2b28-4603-953e-1e5efd56107d/MES_RULES.md)

### ✅ Decision 3: GitFlow Workflow (main/develop/feature/release)
**Date:** 2025-01-27  
**Rationale:** Clear separation: universal template vs factory-specific code  
**Implementation:** Protected branches, PR required  
**Document:**  GIT_WORKFLOW.md [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_27c490ee-2624-4094-bd8d-c6940628e2ff/7e0c3217-abbd-45d3-ba13-e8c9649277c9/GIT_WORKFLOW.md)

### ✅ Decision 4: 90%+ Test Coverage Requirement
**Date:** 2025-01-20  
**Rationale:** Production stability, regression prevention  
**Current:** 93% global, 91% DSIZ ✅  
**Document:**  MES_RULES.md [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_27c490ee-2624-4094-bd8d-c6940628e2ff/7a38f3bb-2b28-4603-953e-1e5efd56107d/MES_RULES.md)

### ✅ Decision 5: No Direct Changes to template-base
**Date:** 2025-01-20  
**Rationale:** Maintain universal template integrity  
**Process:** GitHub Issue with label "template-update" required  
**Document:**  GIT_WORKFLOW.md [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_27c490ee-2624-4094-bd8d-c6940628e2ff/7e0c3217-abbd-45d3-ba13-e8c9649277c9/GIT_WORKFLOW.md)

### ✅ Decision 6: Context Persistence System
**Date:** 2025-01-27  
**Rationale:** Prevent AI context loss between dialogs  
**Implementation:** MASTER_PROMPT.md + CONTEXT_STACK.md  
**Document:**  MASTER_PROMPT.md,  CONTEXT_STACK.md [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_27c490ee-2624-4094-bd8d-c6940628e2ff/4d433473-167f-4242-9b53-a00faa83d74f/MASTER_PROMPT.md)

***

## 📞 CONTACTS & ESCALATION

### Development Team
```
Lead Developer:  Bezngor
GitHub:          @Bezngor
Repository:      github.com/Bezngor/MES_midex
```

### Escalation Matrix
| Issue Type | Severity | Action | Document |
|------------|----------|--------|----------|
| Git merge conflict | High | Resolve locally, don't force push |  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_27c490ee-2624-4094-bd8d-c6940628e2ff/7e0c3217-abbd-45d3-ba13-e8c9649277c9/GIT_WORKFLOW.md) GIT_WORKFLOW.md |
| Red test blocking | Critical | Fix before commit |  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_27c490ee-2624-4094-bd8d-c6940628e2ff/7a38f3bb-2b28-4603-953e-1e5efd56107d/MES_RULES.md) MES_RULES.md #4 |
| Core modification needed | High | GitHub Issue + template-update label |  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_27c490ee-2624-4094-bd8d-c6940628e2ff/7e0c3217-abbd-45d3-ba13-e8c9649277c9/GIT_WORKFLOW.md) GIT_WORKFLOW.md |
| Production crash | Critical | Hotfix branch + emergency tag |  [ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_27c490ee-2624-4094-bd8d-c6940628e2ff/7e0c3217-abbd-45d3-ba13-e8c9649277c9/GIT_WORKFLOW.md) GIT_WORKFLOW.md (Rollback) |
| API contract break | High | Semantic versioning + update docs | API_SPEC.md |
| Database schema break | High | Alembic migration + downtime planning | DEPLOYMENT.md |

***

## 🔄 MANIFEST UPDATE PROTOCOL

### Когда обновлять
- При создании нового feature/release tag
- При изменении production version
- При завершении фазы разработки
- При архитектурных решениях
- При изменении инфраструктуры
- При критичных багах/hotfix

### Как обновлять
```bash
# 1. Отредактируй PROJECT_MANIFEST.md локально
# 2. Обнови раздел "Last Updated" timestamp
# 3. Commit
git add .cursor/docs/PROJECT_MANIFEST.md
git commit -m "docs: update PROJECT_MANIFEST (v1.x.0-dsiz release)"

# 4. Push в main (через PR если protected)
git push origin main
```

### Синхронизация с CONTEXT_STACK.md
```
CONTEXT_STACK.md    → Детальный snapshot текущего состояния (обновляется каждый день)
PROJECT_MANIFEST.md → High-level overview + changelog (обновляется при release)
```

***

## ✅ MANIFEST INTEGRITY CHECKLIST

Перед обновлением манифеста проверь:

```
[ ] Production Version актуальна?
[ ] Все активные ветки перечислены?
[ ] Последние теги добавлены?
[ ] Фазы разработки актуальны?
[ ] Метрики обновлены?
[ ] Архитектурные решения задокументированы?
[ ] Критичные правила неизменны?
[ ] Ссылки на [file:X] корректны?
[ ] Timestamp обновлён?
```

**Если все ✅ — Manifest готов к commit!**

***

**Version:** 1.0  
**Created:** 2026-01-28  
**Project:** MES Platform v2.1.0 DSIZ  
**GitHub:** https://github.com/Bezngor/MES_midex  
**Production:** https://mes-midex-ru.factoryall.ru  

**Maintainer:** MES Development Team  
**Next Review:** 2026-01-30 (v1.2.0-dsiz release)

***
