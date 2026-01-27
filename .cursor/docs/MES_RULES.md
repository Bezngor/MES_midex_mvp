# MES PLATFORM — 5 ОСНОВНЫХ ПРАВИЛ (v2.0, 27.01.2026)

## 0. Cursor + Termius
**0.1** Всё, что можно в Cursor — **делать в Cursor** (через полный промпт).  
**0.2** Команды на VPS — **ТОЛЬКО через Termius** (явно указывать: "в Termius").

---

## 1. GitOps Workflow

**ЗАКОН**: Все изменения через Git. Никаких прямых правок на сервере!

### Локальная разработка (feature-ветка)

```bash
# Создаём feature-ветку от develop
git checkout develop
git pull origin develop
git checkout -b feat/new-feature

# Разработка → коммиты
git add .
git commit -m "feat: описание изменения"

# Push feature-ветки
git push origin feat/new-feature

# Создай Pull Request на GitHub: feat/new-feature → develop
# После approve и merge → удали feature-ветку
```

### Деплой на Production (через release)

```bash
# Создаём release-ветку от develop
git checkout develop
git pull origin develop
git checkout -b release/v1.x.0-dsiz

# Bump version, обновляем CHANGELOG
git commit -am "chore: prepare release v1.x.0"
git push origin release/v1.x.0-dsiz

# PR на GitHub: release/v1.x.0-dsiz → main
# После merge в main — создаём production tag
git checkout main
git pull origin main
git tag -a v1.x.0-dsiz -m "Release v1.x.0: описание"
git push origin v1.x.0-dsiz

# Деплой на VPS (в Termius)
ssh root@155.212.184.11
cd /opt/mes-platform
git fetch --all --tags
git checkout main
git pull origin main
docker compose -f docker-compose.production.yml restart

# Health check
curl https://mes-midex-ru.factoryall.ru/api/v1/health
```

### Commit Convention (Conventional Commits)

- `feat:` — новая функциональность
- `fix:` — исправление бага
- `docs:` — документация
- `refactor:` — рефакторинг
- `test:` — тесты
- `chore:` — инфраструктура

**Scope**: `feat(dsiz):`, `fix(mrp):`, `docs(readme):` и т.д.

**Подробнее**: См. `.cursor/docs/GIT_WORKFLOW.md`

---

## 2. Модульная архитектура

**ЗАКОН**: `backend/core/` — НЕ ИЗМЕНЯТЬ! Это универсальное ядро.

### Кастомизация БЕЗ кода
- `config/factory_config.yaml` — настройки через YAML

### Кастомизация С кодом
- `backend/customizations/dsiz/` — наследование + DI
- Пример: `DSIZMRPService(MRPService)` → override методов
- DI в `backend/src/main.py`: `app.dependency_overrides[MRPService] = DSIZMRPService`

**Подробнее**: См. `CUSTOMIZATION_GUIDE.md`

---

## 3. MES Терминология (обязательна!)

| Термин | Описание | Таблица |
|--------|----------|---------|
| **ManufacturingOrder** | Производственный заказ | `manufacturing_orders` |
| **WorkCenter** | Рабочий центр (станок) | `work_centers` |
| **ProductionTask** | Задача на операцию | `production_tasks` |
| **BOM** | Bill of Materials | `bill_of_materials` |
| **Batch** | Партия (process mfg) | `batches` |
| **WIP** | Work-in-Process | — |

**ЗАПРЕЩЕНО**: "Заказ" вместо ManufacturingOrder, "Станок" вместо WorkCenter.

---

## 4. Тестирование обязательно

```bash
# DSIZ-специфичные тесты (90%+ coverage)
pytest tests/customizations/dsiz/ -v

# Все тесты (93%+ global coverage)
pytest tests/ --cov=backend --cov-report=html
```

**ЗАКОН**: Красные тесты = НЕ деплоить! ❌

**Target**: 90%+ для критических модулов (MRP, Dispatching).

---

## 5. API Design

### Базовый префикс
- `/api/v1`

### Response формат
```json
// Success
{"success": true, "data": {...}}

// Error
{"success": false, "error": "message"}
```

### HTTP Codes
- `200` — OK
- `201` — Created
- `400` — Validation Error
- `404` — Not Found
- `500` — Server Error

**Подробнее**: См. `API_SPEC.md`

---

## 🚨 Запрещённые действия

| ❌ Нельзя | ✅ Вместо этого |
|-----------|----------------|
| Коммитить прямо в `main` | Создать `hotfix/*` → PR → merge |
| Коммитить прямо в `develop` | Создать `feat/*` → PR → merge |
| Изменять `backend/core/` | Используй `backend/customizations/` |
| Изменять `template-base` | Только через согласование |
| Force-push в protected ветки | Никогда! (только с backup) |
| Править файлы на VPS напрямую | Только через Git → push → pull |

---

## 📞 Связанные документы

- **GIT_WORKFLOW.md** — подробный Git workflow
- **CUSTOMIZATION_GUIDE.md** — как кастомизировать
- **DEPLOYMENT.md** — production deployment
- **TESTING.md** — тестирование
- **API_SPEC.md** — API спецификация

---

**Версия:** 2.0 (27.01.2026)  
**Changelog:**
- v2.0: Обновлён GitOps workflow (main/develop/feature/release), удалено устаревшее Правило #6
- v1.0: Первая версия (26.01.2026)

***

## 📊 Изменения в MES_RULES.md v2.0

| Что изменено | Было | Стало |
|--------------|------|-------|
| **Правило #1** | Упоминание `deployment.sh` | Полный GitOps workflow (feature → develop → release → main) |
| **Правило #6** | Автодеплой через `deployment.sh` | ❌ УДАЛЕНО (дублирование) |
| **Количество правил** | 6 | 5 (0-5) |
| **Ссылки** | Нет | Добавлены ссылки на GIT_WORKFLOW.md и др. |
| **Версия** | v1.0 | v2.0 |
| **IP сервера** | 155.212.184.11 | 155.212.184.11 ✅ |

***
