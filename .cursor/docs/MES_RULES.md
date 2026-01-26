# MES PLATFORM — 6 ОСНОВНЫХ ПРАВИЛ (v1.0, 26.01.2026)

## 0. Cursor + Termius
**0.1** Всё, что можно в Cursor — **Cursor** (полный промпт).
**0.2** VPS команды **ТОЛЬКО Termius** (явно указывать).

## 1. GitOps Workflow
**ВСЕ изменения → Git** (никаких правок на сервере!):
git add . && git commit -m "feat/fix: описание"
git push origin develop/feat/xxx
ssh root@185.177.94.29 "cd /opt/mes-platform && ./deployment.sh feat/xxx"

text

## 2. Модульная архитектура
**НЕ ИЗМЕНЯТЬ** `backend/core/`!
- **config/factory_config.yaml** — без кода.
- **backend/customizations/** — наследование + DI (`main.py`).

## 3. MES Терминология
| ManufacturingOrder | Производственный заказ |
| WorkCenter | Рабочий центр |
| ProductionTask | Задача |
| BOM | Спецификация |
| Batch | Партия |

## 4. Тестирование
pytest tests/customizations/dsiz/ -v # 90%+
pytest tests/ --cov=backend --cov-report=html # 93% global

text
**Красные тесты = НЕ деплоить!**

## 5. API Design
- `/api/v1`
- `{"success": true, "data": {...}}`
- 200/201/400/404/500

## 6. Автодеплой (новое!)
**ТОЛЬКО `./deployment.sh <branch>`** на VPS:
cd /opt/mes-platform
./deployment.sh feat/dsiz-phase1-mrp

text
**НЕТ** ручных `docker compose/alembic/git pull`.

---
**Источник:** MES Space Instructions + DSIZ Phase 2 Lessons.