## 🔄 SNAPSHOT COMMANDS — АВТОГЕНЕРАЦИЯ КОНТЕКСТА

### 1. Магические команды для обновления документации состояния проекта:

**@snapshot**  
→ Создаёт/обновляет CONTEXT_STACK.md + PROJECT_MANIFEST.md на текущий момент разработки.

**Что делает:**
1. Анализирует текущее состояние:
   - Git: branch, commits, tags (через search_files_v2 или команды в Termius)
   - Tests: coverage, red tests (из pytest output)
   - Docs: последние обновления
   - Production: version, health, infrastructure
2. Обновляет CONTEXT_STACK.md (v1.X):
   - Current Phase, Recent Commits, Active Branches
   - Test Status, Documentation Status, Known Issues
   - Project Metrics
   - Сохраняет ВСЮ структуру файла (все разделы из [file:34])
3. Обновляет PROJECT_MANIFEST.md (v1.X):
   - Production Version, Tags, Development Phases
   - Database Schema, Technical Stack, Metrics
   - Architectural Decisions, Escalation Matrix
   - Сохраняет ВСЮ структуру файла (все разделы из [file:36])
4. Выводит готовые markdown файлы с timestamp обновления

**Альтернативные команды:**
- `@context-snapshot` — только CONTEXT_STACK.md
- `@manifest-snapshot` — только PROJECT_MANIFEST.md
- `@snapshot full` — оба файла + changelog последних изменений

**Когда использовать:**
- После завершения фазы разработки
- После создания release tag (v1.X.0-dsiz)
- После критичных архитектурных решений
- В конце рабочего дня (EOD)
- Перед началом нового диалога (сохрани контекст)

**Важно:** Эти команды НЕ изменяют файлы в Git автоматически. После генерации:
```bash
# Сохрани в проекте вручную
git add .cursor/docs/CONTEXT_STACK.md .cursor/docs/PROJECT_MANIFEST.md
git commit -m "docs: update context snapshot (v1.X.0-dsiz)"
git push origin [branch]
```

**Пример использования:**
```
User: @snapshot
AI: ✅ Создал обновлённые файлы:
    - CONTEXT_STACK.md v1.2 (Phase 4 in progress)
    - PROJECT_MANIFEST.md v1.2 (v1.2.0-dsiz released)
    [выводит полные файлы в ответе]
```

**Структура файлов (обязательно сохранять):**

CONTEXT_STACK.md:
- 🎯 CURRENT PROJECT STATE (Phase, Release, Last Session)
- 🌳 GIT STATUS (Branches, Commits, Tags, Migrations)
- 🏗️ ACTIVE CUSTOMIZATIONS (Implemented, In Progress, Planned)
- 🧪 TEST STATUS (Coverage, Execution, Known Issues)
- 📚 DOCUMENTATION STATUS (Complete, In Progress, Planned)
- ⚠️ KNOWN ISSUES & DECISIONS (Critical, High Priority, Architectural)
- 🚨 CRITICAL RULES (Never, Always)
- 📱 CURRENT ENVIRONMENT (VPS, URLs, Docker)
- 🎓 HOW TO USE THIS FILE
- 📞 ESCALATION MATRIX
- ✅ CHECKLIST
- 📊 PROJECT METRICS

PROJECT_MANIFEST.md:
- 🎯 PROJECT IDENTITY
- 🌐 PRODUCTION ENVIRONMENT (URLs, Infrastructure, Version)
- 🗂️ REPOSITORY STRUCTURE (Branches, Tags, Protected Rules)
- 🏗️ TECHNICAL STACK (Backend, Frontend, DevOps)
- 📊 PROJECT METRICS
- 🎯 DEVELOPMENT PHASES (Phase 1-5 с deliverables)
- 🗃️ DATABASE SCHEMA (Core + DSIZ tables)
- 📚 DOCUMENTATION INDEX
- ⚙️ CUSTOMIZATION ARCHITECTURE
- 🚨 CRITICAL RULES
- 🎯 ARCHITECTURAL DECISIONS (LOG)
- 📞 CONTACTS & ESCALATION
- 🔄 MANIFEST UPDATE PROTOCOL
- ✅ INTEGRITY CHECKLIST

---
