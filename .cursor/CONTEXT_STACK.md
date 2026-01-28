# MES Development Context Stack (текущее состояние)

## PHASE INFORMATION
- **Current Phase**: Phase 2 (Backend API + DSIZ Customization)
- **Last Task**: feat/dsiz-qr-tracking (PR #123, merged to develop)
- **Next Task**: Phase 3 (Frontend DSIZ UI)
- **Release Target**: v1.2.0-dsiz (Jan 30, 2026)

## GIT STATUS
- **Current Branch**: develop (last pull: 2026-01-27 14:00 UTC)
- **Open PRs**: 
  - feat/dsiz-workforce-ui (9 commits, 85 coverage)
  - feat/dsiz-planning-api (4 commits, pending review)
- **Production**: main@v1.0.0-dsiz (stable)
- **DB Version**: alembic_version=20260125_dsiz_phase2_tables

## ACTIVE CUSTOMIZATIONS
- ✅ DSIZMRPService (priority logic, batch conflicts)
- ✅ WorkCenterDowntimeTracking (4 new tables)
- ✅ ERP Integration (1C sync, pending auth)
- 🚧 QR Labeling (in progress, 60% done)
- 📋 Workforce Rules (design done, dev pending)

## KNOWN ISSUES & DECISIONS
- ❌ Issue #87: MRP crash with None batch_size → hotfix/fix-mrp-none (ready)
- ✅ Decision: Use DI override pattern (decided 25.01) → no core changes
- ✅ Decision: YAML config for all factory settings → no hardcode

## TESTS STATUS
- Global Coverage: 93%
- DSIZ Coverage: 91% (target: 95%)
- Red Tests: 0 ✅
- Last Run: 2026-01-27 14:00, pytest tests/ --cov

## DOCUMENTATION
- ✅ MES_RULES.md v2.0 (updated 27.01)
- ✅ GIT_WORKFLOW.md v1.1 (updated 27.01)
- ✅ CUSTOMIZATION_GUIDE.md v1.0 (stable)
- ✅ DSIZ_CUSTOMIZATION_#1-7.md (all phases)
- 📋 DEPLOYMENT.md (WIP, Phase 3)

---

**Как использовать:**
При начале нового диалога просто скажи:
