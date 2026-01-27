# Git Workflow для MES Platform (v1.1, 27.01.2026)

## 🎯 Философия

MES Platform использует **GitFlow-подобный workflow** с чёткой изоляцией универсального шаблона и factory-specific кастомизаций.

---

## 🌳 Структура веток

### Постоянные ветки

| Ветка | Назначение | Защита | Merge из |
|-------|-----------|--------|----------|
| `main` | **Production** — только стабильные релизы | 🔒 Protected | `release/*` |
| `develop` | **Integration** — сборка всех фич | 🔒 Protected | `feat/*`, `fix/*` |
| `template-base` | **Универсальный шаблон** — READ-ONLY | 🔒 Protected | ❌ Никогда |

### Временные ветки

| Префикс | Назначение | Создаётся от | Мержится в | Удаляется после merge |
|---------|-----------|--------------|------------|----------------------|
| `feat/*` | Новая функциональность | `develop` | `develop` | ✅ Да |
| `fix/*` | Исправление бага | `develop` или `main` | `develop` или `main` | ✅ Да |
| `release/*` | Подготовка релиза | `develop` | `main` + `develop` | ✅ Да |
| `hotfix/*` | Срочное исправление production | `main` | `main` + `develop` | ✅ Да |

---

## 🔄 Жизненный цикл разработки

### 1. Начало новой фичи

```bash
# Переключаемся на develop и обновляем
git checkout develop
git pull origin develop

# Создаём feature-ветку
git checkout -b feat/dsiz-qr-tracking

# Работаем, коммитим
git add backend/customizations/dsiz/services/qr_service.py
git commit -m "feat(dsiz): add QR tracking service"

# Push в удалённый репозиторий
git push origin feat/dsiz-qr-tracking
```

### 2. Завершение фичи (через Pull Request)
GitHub → Pull Request:
- Base: develop
- Compare: feat/dsiz-qr-tracking
- Review → Approve → Squash and Merge

Локально после merge:

```bash
git checkout develop
git pull origin develop
git branch -d feat/dsiz-qr-tracking  # Удаляем локальную ветку
git push origin --delete feat/dsiz-qr-tracking  # Удаляем remote ветку
```

### 3. Создание релиза
```bash
# Создаём release-ветку от develop
git checkout develop
git pull origin develop
git checkout -b release/v1.1.0-dsiz

# Обновляем версию в файлах
# - backend/src/__init__.py: __version__ = "1.1.0"
# - frontend/package.json: "version": "1.1.0"
git commit -am "chore: bump version to 1.1.0"

# Push release-ветки
git push origin release/v1.1.0-dsiz

# Merge в main (через PR на GitHub)
# Base: main, Compare: release/v1.1.0-dsiz

# После merge в main — создаём tag
git checkout main
git pull origin main
git tag -a v1.1.0-dsiz -m "DSIZ Release v1.1.0: QR tracking + Workforce UI"
git push origin v1.1.0-dsiz

# Merge обратно в develop (чтобы version bump был там)
git checkout develop
git merge main --no-ff -m "chore: merge release v1.1.0 back to develop"
git push origin develop
```

### 4. Hotfix на production
```bash
# Срочный баг на production
git checkout main
git pull origin main
git checkout -b hotfix/fix-mrp-crash

# Исправляем баг
git add backend/customizations/dsiz/services/dsiz_mrp_service.py
git commit -m "fix(dsiz): handle None in MRP batch calculation"

# Merge в main
git checkout main
git merge hotfix/fix-mrp-crash --no-ff
git tag -a v1.0.1-dsiz -m "Hotfix: MRP crash fix"
git push origin main v1.0.1-dsiz

# Merge в develop (чтобы фикс не потерялся)
git checkout develop
git merge hotfix/fix-mrp-crash --no-ff
git push origin develop

# Удаляем hotfix-ветку
git branch -d hotfix/fix-mrp-crash
```

📜 **Правила коммитов**
*Формат (Conventional Commits)*
```text
<type>(<scope>): <subject>

<body>

<footer>
```

*Типы*
| Тип      | Описание                            | Пример                                  |
| -------- | ----------------------------------- | --------------------------------------- |
| feat     | Новая функциональность              | feat(dsiz): add QR tracking             |
| fix      | Исправление бага                    | fix(mrp): handle empty inventory        |
| docs     | Документация                        | docs: update GIT_WORKFLOW.md            |
| refactor | Рефакторинг без изменения поведения | refactor(dsiz): extract workforce logic |
| test     | Добавление/исправление тестов       | test(dsiz): add MRP service tests       |
| chore    | Инфраструктурные изменения          | chore: bump version to 1.1.0            |

*Scope (область)*
- dsiz — DSIZ-специфичные изменения
- core — изменения в универсальном ядре (⚠️ требует согласования!)
- mrp, dispatching, frontend — модули
- Без scope — глобальные изменения (deploy, CI/CD)

🚫 **Запрещённые действия**
| ❌ Нельзя                     | ✅ Вместо этого                                 |
| ---------------------------- | ---------------------------------------------- |
| Коммитить прямо в main       | Создать hotfix/* → PR → merge                  |
| Коммитить прямо в develop    | Создать feat/* → PR → merge                    |
| Изменять template-base       | Только через отдельный процесс template update |
| Force-push в protected ветки | Никогда! Используй revert или hotfix           |
| Мержить без тестов (CI red)  | Дождись зелёных тестов                         |

🔧 **Rollback (откат)**
*Откат последнего deploy*
```bash
# На VPS
ssh root@155.212.184.11
cd /opt/mes-platform

# Смотрим историю тегов
git tag -l "v*-dsiz" --sort=-version:refname | head -5

# Откатываемся на предыдущий tag
git checkout v1.0.0-dsiz  # Предыдущая версия
docker compose -f docker-compose.production.yml restart

# Проверяем
curl http://localhost:8002/api/v1/health
```

*Откат фичи (revert merge)*
```bash
# Локально
git checkout develop
git log --oneline -10  # Находим merge commit фичи

# Revert merge commit
git revert -m 1 <merge-commit-sha>
git push origin develop

# Deploy
ssh root@155.212.184.11 "cd /opt/mes-platform && git pull && docker compose restart"
```

📊 **Проверка перед merge**
*Pre-merge Checklist*
- Все тесты зелёные (pytest backend/tests/)
- Coverage ≥ 90% для новых модулей
- Нет конфликтов с develop
- Коммиты следуют Conventional Commits
- Документация обновлена (если нужно)
- .env.example обновлён (если добавлены переменные)
- Alembic миграции созданы (если изменена БД)

🎯 **Примеры**
Пример 1: Добавление DSIZ модуля (Phase 4)
```bash
git checkout develop
git pull origin develop
git checkout -b feat/dsiz-phase4-dragdrop

# Разработка...
git add frontend/src/components/dsiz/DraggableGantt.tsx
git commit -m "feat(dsiz): add drag&drop to Gantt chart"

git add backend/tests/customizations/dsiz/test_gantt_api.py
git commit -m "test(dsiz): add Gantt API tests (95% cov)"

git push origin feat/dsiz-phase4-dragdrop

# GitHub PR: feat/dsiz-phase4-dragdrop → develop
# После merge:
git checkout develop && git pull
git branch -d feat/dsiz-phase4-dragdrop
```

Пример 2: Release v1.2.0
```bash
git checkout -b release/v1.2.0-dsiz develop
# Bump version, update CHANGELOG
git commit -am "chore: prepare release v1.2.0"
git push origin release/v1.2.0-dsiz

# GitHub PR: release/v1.2.0-dsiz → main
# После merge в main:
git checkout main && git pull
git tag -a v1.2.0-dsiz -m "Release v1.2.0: Drag&drop Gantt"
git push origin v1.2.0-dsiz

# Merge обратно в develop
git checkout develop
git merge main --no-ff
git push origin develop
```

📞 **Эскалация**
Критичные изменения требуют согласования:
- Изменения в backend/core/ (универсальное ядро)
- Изменения в template-base
- Database schema breaking changes
- Force-push в protected ветки

Обращайтесь: GitHub Issues → label critical-review

Версия: 1.1 (27.01.2026)
Автор: MES Platform Team
Связанные документы: MES_RULES.md, CUSTOMIZATION_GUIDE.md, DEPLOYMENT.md