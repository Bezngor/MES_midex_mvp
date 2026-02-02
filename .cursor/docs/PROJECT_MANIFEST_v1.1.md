# 📋 MES PLATFORM PROJECT MANIFEST v1.1

**Last Updated:** 2026-01-29 08:02 MSK  
**Status:** Production Stable (v1.1.0-dsiz)  
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
Production:  https://mes-midex-ru.factoryall.ru ✅ LIVE
Planning:    https://mes-midex-ru.factoryall.ru/dsiz/planning ✅ NEW (Phase 3)
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
Proxy:       Traefik v3.6.1 (Dokploy) ✅ FIXED (29.01)
Database:    PostgreSQL 13 (Supabase)
Cache:       Redis 7
Monitoring:  n8n workflows (n8n.factoryall.ru)
```

### Current Production Version
```
Tag:         v1.1.0-dsiz ✅ NEW
Branch:      main (26826a7)
Release:     29.01.2026
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
| **main** | Production | 🔒 Protected | 26826a7 (v1.1.0-dsiz) ✅ NEW |
| **develop** | Integration | 🔒 Protected | [ahead of main] |
| **template-base** | Universal template | 🔒 READ-ONLY | f08fd2b (v2.1.0-template) |

### Tags
```
Production:
  v1.1.0-dsiz                   (29.01.2026) — Phase 3 Frontend COMPLETE ✅ NEW
  v1.0.0-dsiz                   (27.01.2026) — Phase 2 Backend complete

Template:
  v2.1.0-template               (19.01.2026) — Universal MES template

Backups:
  backup-develop-2026-01-27     — Safety backup
  backup-main-2026-01-27        — Safety backup
```

### Protected Branch Rules
```
main:
  - Merge only from release/* branches
  - Require PR approval (#1 ✅ merged)
  - Require status checks (CI green)
  - No force push
  - No deletion

develop:
  - Merge only from feat/*, fix/*, release/* branches
  - Require PR approval
  - No force push
  - No deletion

template-base:
  - READ-ONLY (no direct pushes)
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

### Frontend ✅ Phase 3 Complete
```
Framework:       React 18.2+
Language:        TypeScript 5.0+
Build:           Vite 5.0+
State:           React Query + Context API
UI:              Tailwind CSS 3+
Charts:          Recharts (Gantt chart)
Forms:           React Hook Form + Zod
Testing:         Manual QA ✅ (Jest/RTL planned Phase 4)
Bundle Size:     ~275KB (minified, gzipped)
```

### DevOps
```
Containerization: Docker + Docker Compose
CI/CD:           GitHub Actions (planned Phase 5)
Deployment:      GitOps (git pull + docker restart)
Logging:         Docker logs + n8n monitoring
Secrets:         .env files (gitignored)
Reverse Proxy:   Traefik v3.6.1 (via Dokploy)
```

***

## 📊 PROJECT METRICS (Current — 29.01.2026)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Test Coverage (Global)** | 93%+ | 93% | ✅ Met |
| **Test Coverage (DSIZ)** | 91%+ | 91% | ✅ Met |
| **Red Tests** | 0 | 0 | ✅ Met |
| **API Endpoints** | 50+ | 60+ | ✅ Exceeded |
| **Database Tables** | 10+ | 13 | ✅ Exceeded |
| **Frontend Components (DSIZ)** | 5+ | 5 | ✅ Met |
| **Code in core/ (from DSIZ)** | 0% | 0% | ✅ Met |
| **Config in YAML** | 100% | 100% | ✅ Met |
| **GitOps Compliance** | 100% | 100% | ✅ Met |
| **Documentation Complete** | 100% | 100% | ✅ Met |
| **Phase 3 Progress** | 100% | 100% | ✅ Complete |

***

## 🎯 DEVELOPMENT PHASES

### ✅ Phase 1: Template Creation (19-23.01.2026)
**Status:** Complete  
**Tag:** v2.1.0-template  

### ✅ Phase 2: DSIZ Backend + API (23-26.01.2026)
**Status:** Complete  
**Tag:** v1.0.0-dsiz  

### ✅ Phase 3: DSIZ Frontend (26-29.01.2026) ✅ NEW
**Status:** Complete  
**Tag:** v1.1.0-dsiz  
**Deliverables:**
- ✅ DsizPlanningPage (`/dsiz/planning`) — форма планирования реакторов
- ✅ ReactorSlotSelector — выбор 12 слотов реакторов
- ✅ WorkforceInput — ввод персонала по сменам (OPERATOR, PACKER, AUTO)
- ✅ LabelingModeSelector — режим маркировки (AUTO/MANUAL)
- ✅ DsizGanttChart — визуализация операций
- ✅ useDsizPlanning Hook — интеграция с API `/dsiz/planning/run`
- ✅ Navigation routes (DSIZ Planning, Shift Actualize, Master Data)
- ✅ Production deployment (v1.1.0-dsiz)
- ✅ Traefik troubleshooting resolved

**Critical Issues Resolved:**
1. Git: develop/main mismatch → GitFlow release cycle
2. Docker: Bundle cache → Hard rebuild (--no-cache)
3. Infrastructure: Systemd Nginx blocked port 80 → systemctl stop/disable

### 📋 Phase 4: Advanced Features (30.01 - 03.02.2026)
**Status:** Planned  
**ETA:** v1.2.0-dsiz (03.02.2026)  
**Scope:**
- Interactive Gantt chart (drag & drop)
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
work_centers               — рабочие центры
production_tasks           — задачи на операции
inventory_balances         — остатки сырья/ГП
inventory_transactions     — движения склада
shifts                     — смены
users                      — пользователи
```

### DSIZ Tables (Customization, 7 tables)
```
work_center_modes          — режимы РЦ (REACTOR/AUTO/MANUAL)
changeover_matrix          — матрица переналадок
base_rates                 — базовые нормы (кг/час)
workforce_requirements     — нормы персонала
labeling_rules             — правила маркировки (QR)
qr_availability            — наличие QR-меток
product_routing            — маршруты
```

### Migrations
```
Latest:  20260125_dsiz_phase2_tables (27.01.2026)
Status:  ✅ Applied to production
Tool:    Alembic
```

***

## 📚 DOCUMENTATION INDEX

### Core Documentation (✅ Complete — 29.01.2026)
| Файл | Версия | Описание |
|------|--------|----------|
| `README.md` | v2.1.0 | Project overview |
| `MES_RULES.md` | v2.0 | 5 core rules (27.01) |
| `GIT_WORKFLOW.md` | v1.1 | Git process (27.01) |
| `CUSTOMIZATION_GUIDE.md` | v2.1.0 | DI pattern, 4 scenarios |
| `MASTER_PROMPT.md` | v1.0 | AI development rules (27.01) |
| `CONTEXT_STACK.md` | v1.1 | State machine (29.01) ✅ NEW |
| `PROJECT_MANIFEST.md` | v1.1 | THIS file (29.01) ✅ NEW |

### DSIZ Specs (✅ Complete)
```
DSIZ_CUSTOMIZATION_#1-7.md     — Phase 1-3 specs
DSIZ_TEST_GENERATION_GUIDE.md  — Test standards
DSIZ_DEPLOYMENT_LESSONS.md     — Phase 2+3 lessons ✅ UPDATED
```

### In Progress (🚧 70%)
```
DEPLOYMENT.md             — Production deployment guide (70%)
ROLLBACK_PROCEDURES.md    — Emergency procedures (design phase)
```

***

## ⚙️ CUSTOMIZATION ARCHITECTURE

### Pattern: Dependency Injection (DI)
```
✅ backend/core/              → Universal template (READ-ONLY)
✅ backend/customizations/dsiz/ → DSIZ-specific (DI + inheritance)
✅ frontend/src/components/dsiz/ → DSIZ React components ✅ NEW
✅ frontend/src/pages/DsizPlanningPage.tsx → Main UI ✅ NEW
✅ config/factory_config.yaml → YAML config
❌ backend/core/ changes      → PROHIBITED
```

### Active Customizations (Phase 3 COMPLETE)
| Module | Status | Coverage | Location |
|--------|--------|----------|----------|
| **DSIZMRPService** | ✅ Complete | 94% | `customizations/dsiz/services/mrp_service.py` |
| **BatchConflictDetection** | ✅ Complete | 92% | `customizations/dsiz/services/batch_conflict_*.py` |
| **WorkforcePlanning** | ✅ Complete | 88% | `customizations/dsiz/services/workforce_*.py` |
| **DsizPlanningPage** | ✅ Complete | — | `frontend/src/pages/DsizPlanningPage.tsx` ✅ |
| **ReactorSlotSelector** | ✅ Complete | — | `frontend/src/components/dsiz/ReactorSlotSelector.tsx` ✅ |
| **WorkforceInput** | ✅ Complete | — | `frontend/src/components/dsiz/WorkforceInput.tsx` ✅ |
| **LabelingModeSelector** | ✅ Complete | — | `frontend/src/components/dsiz/LabelingModeSelector.tsx` ✅ |
| **DsizGanttChart** | ✅ Complete | — | `frontend/src/components/dsiz/DsizGanttChart.tsx` ✅ |

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
✅ Работать в feat/* или fix/* ветках
✅ Pull Request обязательны (feat/* → develop)
✅ Release через release/* → main (PR #1 ✅)
✅ Тегировать production после merge в main
✅ Conventional Commits (feat:, fix:, docs:)
✅ Деплой только из main (git pull + docker restart)
```

### Testing Rules
```
✅ Минимум 90% coverage для DSIZ модулей
✅ Минимум 93% global coverage
✅ 0 red tests перед commit
✅ Тесты для всей бизнес-логики
✅ Pytest перед каждым push
```

***

## 🎯 ARCHITECTURAL DECISIONS (LOG)

### ✅ Decision 1-6: See Previous Manifest

### ✅ Decision 7: GitFlow Release Cycle ✅ NEW
**Date:** 2026-01-29  
**Rationale:** Prevent localhost/production divergence  
**Implementation:** develop → release/v1.1.0-dsiz → main (PR #1)  
**Document:** GIT_WORKFLOW.md v1.1

### ✅ Decision 8: Hard Rebuild for Frontend Changes ✅ NEW
**Date:** 2026-01-29  
**Rationale:** Docker cache causes stale bundles  
**Command:** `docker rmi -f <image>` + `docker compose build --no-cache --pull`  
**Document:** DSIZ_DEPLOYMENT_LESSONS.md (Issue #3)

### ✅ Decision 9: Systemd Nginx Disabling ✅ NEW
**Date:** 2026-01-29  
**Rationale:** Free port 80 for Traefik (Dokploy proxy)  
**Command:** `systemctl stop nginx && systemctl disable nginx`  
**Document:** DSIZ_DEPLOYMENT_LESSONS.md (Issue #3)

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
| Git merge conflict | High | Resolve locally | GIT_WORKFLOW.md |
| Red test | Critical | Fix before commit | MES_RULES.md #4 |
| Core modification | High | GitHub Issue + template-update | GIT_WORKFLOW.md |
| Production crash | Critical | Hotfix branch + tag | GIT_WORKFLOW.md |
| API break | High | Semantic versioning | API_SPEC.md |
| DB schema break | High | Alembic migration | DEPLOYMENT.md |
| Traefik down | Critical | Check nginx, restart | DSIZ_DEPLOYMENT_LESSONS.md ✅ |

***

## 🔄 MANIFEST UPDATE PROTOCOL

### Когда обновлять
- При создании feature/release tag
- При изменении production version
- При завершении фазы разработки
- При архитектурных решениях
- При критичных багах/hotfix

### Как обновлять
```bash
# 1. Отредактируй PROJECT_MANIFEST.md
# 2. Обнови timestamp
# 3. Commit
git add .cursor/docs/PROJECT_MANIFEST.md
git commit -m "docs: update PROJECT_MANIFEST (v1.x.0-dsiz)"
git push origin main  # через PR если protected
```

### Magic Command для Автогенерации
```
@snapshot
```
Создаст обновлённые CONTEXT_STACK.md + PROJECT_MANIFEST.md.

***

## ✅ MANIFEST INTEGRITY CHECKLIST

```
[ ] Production Version актуальна? ✅ v1.1.0-dsiz
[ ] Все активные ветки перечислены? ✅
[ ] Последние теги добавлены? ✅ v1.1.0-dsiz
[ ] Фазы разработки актуальны? ✅ Phase 3 Complete
[ ] Метрики обновлены? ✅
[ ] Архитектурные решения задокументированы? ✅ Decision 7-9
[ ] Критичные правила неизменны? ✅
[ ] Timestamp обновлён? ✅ 29.01.2026 08:02
```

**All ✅ — Manifest ready!**

***

**Version:** 1.1  
**Created:** 2026-01-28  
**Updated:** 2026-01-29 08:02 MSK ✅ NEW  
**Project:** MES Platform v2.1.0 DSIZ  
**GitHub:** https://github.com/Bezngor/MES_midex  
**Production:** https://mes-midex-ru.factoryall.ru  

**Maintainer:** MES Development Team  
**Next Review:** 2026-02-03 (v1.2.0-dsiz release)

***
```

***

## 🎯 МАГИЧЕСКАЯ КОМАНДА

**Чтобы обновить оба файла в любой момент, напиши:**

```
@snapshot
```

**Что произойдёт:**
1. AI прочитает текущее состояние проекта (Git, tests, docs, production)
2. Создаст/обновит `CONTEXT_STACK.md` (v1.X)
3. Создаст/обновит `PROJECT_MANIFEST.md` (v1.X)
4. **Сохранит структуру документов** (все разделы)
5. **Обновит данные** (commits, tags, metrics, phases)
6. Выведет готовые файлы в ответе

**Альтернативные команды:**
- `@context-snapshot` — только CONTEXT_STACK.md
- `@manifest-snapshot` — только PROJECT_MANIFEST.md
- `@snapshot full` — оба файла + changelog

***

## ✅ SUMMARY

1. **CONTEXT_STACK.md v1.1** — обновлён (Phase 3 complete, v1.1.0-dsiz, Traefik fix)
2. **PROJECT_MANIFEST.md v1.1** — обновлён (Phase 3 deliverables, Decision 7-9, Infrastructure fixes)
3. **Магическая команда** — `@snapshot` (автогенерация в любой момент)
4. **Структура сохранена** — все разделы, форматирование, таблицы ✅
