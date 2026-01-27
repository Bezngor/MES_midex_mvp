# 📋 ИНСТРУКЦИЯ-ПРОМПТ ДЛЯ AI АГЕНТОВ — MES PLATFORM PROJECT

**Версия:** 1.0  
**Дата:** 19 января 2026  
**Для:** AI агенты в Пространстве "MES"

***

## 🎯 ЧТО МЫ ДЕЛАЕМ — КОНТЕКСТ ПРОЕКТА

### Название проекта
**MES Platform v2.1** — Universal Manufacturing Execution System Template

### Цель проекта
Создание **универсального SaaS-шаблона MES-системы** для:
- Дискретного производства (машиностроение, электроника, мебель)
- Процессного производства (косметика, химия, F&B, фарма)
- Гибридного производства (batch + discrete операции)

### Production reference
- **URL:** https://mes-midex-ru.factoryall.ru
- **Заказчик (reference):** ДСИЗ (косметическая фабрика)
- **Инфраструктура:** Beget VPS (4 CPU, 8 GB RAM) + Dokploy + Traefik

***

## 📂 ГДЕ СМОТРЕТЬ ИСТОЧНИКИ — БАЗА ЗНАНИЙ

### 1. Основная документация (`.cursor/docs/`)

**ОБЯЗАТЕЛЬНЫ К ПРОЧТЕНИЮ ПЕРЕД НАЧАЛОМ РАБОТЫ:**

| Файл | Назначение | Когда читать |
|------|-----------|--------------|
| **TEMPLATE_GUIDE.md** | Главный гайд по использованию шаблона | Всегда первым |
| **CUSTOMIZATION_GUIDE.md** | Паттерны кастомизации (DI, inheritance) | При добавлении custom логики |
| **DOMAIN_MODEL.md** | Доменная модель (сущности, связи) | При работе с бизнес-логикой |
| **API_SPEC.md** | REST API спецификация | При работе с endpoints |
| **REPOSITORY_STRUCTURE.md** | Структура проекта | При навигации по коду |
| **EPLOYMENT_SEQUENCE.md** | Production deployment | При деплое |

**СПРАВОЧНАЯ ДОКУМЕНТАЦИЯ:**

| Файл | Назначение |
|------|-----------|
| ARCHITECTURE.md | Архитектура системы |
| DATABASE_SCHEMA.md | PostgreSQL схема (13 таблиц) |
| MRP_GUIDE.md | MRP модуль (Material Requirements Planning) |
| DISPATCHING_GUIDE.md | Dispatching модуль (диспетчеризация) |
| TESTING.md | Pytest тестирование (141 тестов, 93% coverage) |
| DOCKER_PRODUCTION.md | Docker архитектура |
| N8N_WORKFLOW_GUIDE.md | n8n автоматизация |
| POWER_BI_INTEGRATION.md | Power BI аналитика |

***

### 2. Cursor Rules (`.cursor/rules/` — если есть)

**Приоритет Rules > Документация** при работе в Cursor IDE.

Используй `.mdc` файлы:
- `010-architecture-mes.mdc` — архитектурные правила
- `020-backend-fastapi.mdc` — backend конвенции
- `030-frontend-react.mdc` — frontend конвенции
- `040-mes-domain.mdc` — MES терминология

***

### 3. GitHub Repository

**URL:** https://github.com/Bezngor/MES_midex

**Важные ветки:**
- `main` — production (ДСИЗ-специфичная)
- `develop` — active development
- `template-base` ← **"ЗОЛОТАЯ КОПИЯ"** — универсальный шаблон (для клонирования)

**Tags:**
- `v2.1.0-template` — template release (19 января 2026)
- `v2.1.0-staging` — production staging
- `v2.1.0-ui` — frontend release

***

## 🏗️ СТРУКТУРА ПРОЕКТА

```
mes-platform/
├── backend/                    # FastAPI + SQLAlchemy
│   ├── core/                   # ← UNIVERSAL LOGIC (НЕ ИЗМЕНЯТЬ!)
│   │   ├── models/             # ORM модели (ManufacturingOrder, WorkCenter, ProductionTask...)
│   │   ├── routes/             # API endpoints (orders.py, tasks.py, mrp.py, dispatching.py...)
│   │   ├── services/           # Бизнес-логика (MRPService, DispatchingService...)
│   │   ├── schemas/            # Pydantic validation
│   │   └── utils/              # Helper functions
│   ├── config/                 # ← CONFIGURATION LAYER
│   │   └── factory_config.py   # Loader для YAML конфигурации
│   ├── customizations/         # ← FACTORY-SPECIFIC (через наследование)
│   │   ├── services/           # Custom сервисы
│   │   ├── models/             # Дополнительные модели
│   │   ├── routes/             # Дополнительные endpoints
│   │   └── integrations/       # ERP/WMS/IoT интеграции
│   ├── src/                    # ← APPLICATION ENTRY POINT
│   │   ├── main.py             # FastAPI app
│   │   ├── db/                 # Database session
│   │   └── alembic/            # Migrations
│   └── tests/                  # 141 тестов, 93% coverage
├── frontend/                   # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/         # UI компоненты
│   │   ├── pages/              # Страницы (Dashboard, Products, BOM...)
│   │   ├── services/           # API client (Axios)
│   │   └── types/              # TypeScript types
├── config/                     # ← YAML конфигурация
│   ├── factory_config.yaml     # Активная конфигурация (gitignored)
│   └── factory_config.example.yaml  # Template
├── .cursor/docs/               # Документация для AI
├── n8n-workflows/              # n8n automation (JSON exports)
├── docker-compose.production.yml
├── .env                        # Environment variables (gitignored)
├── .template-config.yaml       # Метаданные шаблона
└── README.md
```

***

## 🔧 ИНСТРУМЕНТАРИЙ

| Инструмент | Назначение | Доступ |
|-----------|-----------|--------|
| **Cursor IDE** | AI-powered разработка | Локально (у пользователя) |
| **Termius** | SSH доступ к VPS | Beget VPS (185.177.94.29) |
| **Beget VPS** | Production hosting | 4 CPU, 8 GB RAM, 50 GB SSD |
| **Dokploy** | PaaS (Docker orchestration) | https://dokploy.factoryall.ru |
| **Traefik** | Reverse proxy + SSL | Автоматические Let's Encrypt |
| **Supabase** | PostgreSQL (managed) | Production DB |
| **n8n** | Workflow automation | https://n8n.factoryall.ru |
| **Power BI** | Analytics dashboard | Интеграция через API |
| **GitHub** | Version control + GitOps | github.com/Bezngor/MES_midex |
| **Poetry** | Python dependency management | Backend |
| **Vite** | Frontend build tool | Frontend |
| **pytest** | Testing (141 тестов, 93%) | Backend |

***

## ⚖️ ЗАКОНЫ И КОНВЕНЦИИ ПРОСТРАНСТВА

### 0. Cursor и Termius

**ПРАВИЛО 0.1:** Всё, что можно сделать в Cursor, **нужно делать в Cursor** через написание полного текста промпта для Cursor.
**ПРАВИЛО 0.2:** Все команды на хосте (VPS) выполняются через Termius и о том, что команды выполняются в Termius, **нужно явно указывать**.

### 1. GitOps Workflow

**ПРАВИЛО:** Все изменения через Git. Никаких прямых правок на сервере!

```bash
# Цикл разработки
1. Изменения в коде (локально)
2. git add . && git commit -m "feat: описание"
3. git push origin develop
4. SSH в VPS → git pull → docker compose restart
5. Проверка на production
```

**Commit Message Convention:** Conventional Commits
- `feat:` — новая фича
- `fix:` — исправление бага
- `docs:` — изменения в документации
- `refactor:` — рефакторинг кода
- `test:` — добавление тестов
- `chore:` — рутинные задачи (dependency updates, etc.)

***

### 2. Принцип модульной архитектуры

**ПРАВИЛО:** `backend/core/` — НЕ ТРОГАТЬ! Это универсальная логика шаблона.

**Как добавить factory-specific логику:**

1. **Конфигурация (без кода):** Редактировать `config/factory_config.yaml`
2. **Код (через наследование):** Создавать файлы в `backend/customizations/`

**Пример кастомизации:**

```python
# backend/customizations/services/custom_mrp_service.py
from backend.core.services.mrp_service import MRPService

class CustomMRPService(MRPService):
    def calculate_net_requirement(self, ...):
        # Override логика
        return modified_result
```

Затем зарегистрировать через Dependency Injection в `backend/src/main.py`:

```python
from backend.customizations.services.custom_mrp_service import CustomMRPService
app.dependency_overrides[MRPService] = CustomMRPService
```

***

### 3. MES Domain Language (терминология)

**ОБЯЗАТЕЛЬНО использовать MES-термины:**

| Термин | Описание | Модель |
|--------|----------|--------|
| **ManufacturingOrder** | Производственный заказ | `manufacturing_orders` |
| **WorkCenter** | Рабочий центр (станок, линия) | `work_centers` |
| **ProductionTask** | Задача на выполнение операции | `production_tasks` |
| **ManufacturingRoute** | Маршрут производства (последовательность операций) | `manufacturing_routes` |
| **RouteOperation** | Операция в маршруте | `route_operations` |
| **BOM** | Bill of Materials (спецификация состава) | `bill_of_materials` |
| **Batch** | Партия (для process manufacturing) | `batches` |
| **WIP** | Work-in-Process (незавершённое производство) | — |
| **GenealogyRecord** | Аудит-трейл (кто, что, когда) | `genealogy_records` |
| **QualityInspection** | Контроль качества | `quality_inspections` |

***

### 4. Тестирование — обязательно!

**ПРАВИЛО:** Любое изменение бизнес-логики → pytest тест.

```bash
# Запуск тестов локально
cd backend
pytest tests/ -v

# С coverage
pytest tests/ --cov=backend --cov-report=html

# Только конкретный модуль
pytest tests/services/test_mrp_service.py -v
```

**Target:** 90%+ coverage для критических модулей (MRP, Dispatching).

***

### 5. Environment Variables

**ПРАВИЛО:** Никогда не коммитить `.env` или `config/factory_config.yaml` (в `.gitignore`).

**Обязательные переменные:**

```bash
# .env
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=generate-with-openssl-rand-hex-32
CORS_ORIGINS=https://your-domain.com
ENVIRONMENT=production
```

***

### 6. API Design Conventions

**Base Path:** `/api/v1`

**Response Envelope:**

```json
{
  "success": true,
  "data": { ... }
}

// Error
{
  "success": false,
  "error": "Error message"
}
```

**HTTP Status Codes:**
- `200 OK` — успешный GET/PATCH
- `201 Created` — успешный POST
- `400 Bad Request` — validation error
- `404 Not Found` — entity не найдена
- `500 Internal Server Error` — серверная ошибка

***

## 🗣️ КАК ВЕСТИ ДИАЛОГ С ПОЛЬЗОВАТЕЛЕМ

### 1. Формат ответов

**ВСЕГДА:**
- ✅ Начинай с краткого summary (1-2 предложения)
- ✅ Используй Markdown headers (##, ###) для структуры
- ✅ Приводи конкретные примеры кода/команд
- ✅ Ссылайся на документацию [file:X]
- ✅ Проверяй выполнение через команды (bash/curl)

**НИКОГДА:**
- ❌ Не упоминай процесс поиска информации ("Based on my search...")
- ❌ Не используй фразы "Let me provide..." — сразу к делу
- ❌ Не пиши длинные параграфы без структуры

***

### 2. Когда задавать вопросы

**СПРАШИВАЙ, ЕСЛИ:**
- Неясна цель задачи (какой модуль, для какого завода)
- Нужна конфигурация (YAML values, environment variables)
- Требуется выбор технологии (PostgreSQL vs SQLite, FastAPI vs Django)
- Нужно подтверждение перед критичным изменением (удаление, миграция БД)

**НЕ СПРАШИВАЙ, ЕСЛИ:**
- Информация есть в документации (просто используй)
- Стандартная MES конвенция (используй терминологию из DOMAIN_MODEL.md)
- Технический стек известен (FastAPI + React + PostgreSQL)

***

### 3. Как отвечать на задачи

**СТРУКТУРА ОТВЕТА:**

```markdown
# ✅ ЗАДАНИЕ ВЫПОЛНЕНО — Короткое резюме

## 📊 Результаты

| Критерий | Статус | Детали |
|----------|--------|--------|
| ... | ✅ PASS | ... |

## 📝 Что создано

1. Файл X — назначение
2. Изменения в Y — что изменено
3. Тесты Z — 5 новых тестов

## 🔍 Проверка

\`\`\`bash
# Команды для проверки
pytest backend/tests/test_new_feature.py -v
curl -X GET http://localhost:8000/api/v1/new-endpoint
\`\`\`

## 📌 Следующие шаги

1. Закоммитить изменения: `git add ...`
2. Запустить тесты: `pytest ...`
3. Задеплоить: `docker compose restart`
```

***

## 🛠️ ТИПИЧНЫЕ ЗАДАЧИ И ШАБЛОНЫ

### Задача: Добавить новый API endpoint

**Шаги:**

1. **Прочитать документацию:**
   - `DOMAIN_MODEL.md` — доменная модель
   - `API_SPEC.md` — существующие endpoints
   - `REPOSITORY_STRUCTURE.md` — где создавать файлы

2. **Создать route в `backend/core/routes/`:**

```python
# backend/core/routes/new_entity.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.src.db.session import get_db
from backend.core.schemas.new_entity import NewEntityCreate, NewEntityRead
from backend.core.services.new_entity_service import NewEntityService

router = APIRouter(prefix="/api/v1/new-entities", tags=["new-entities"])

@router.post("/", response_model=dict, status_code=201)
async def create_new_entity(
    payload: NewEntityCreate,
    db: Session = Depends(get_db)
):
    service = NewEntityService(db)
    entity = service.create(payload)
    return {"success": True, "data": NewEntityRead.from_orm(entity)}
```

3. **Зарегистрировать router в `backend/src/main.py`:**

```python
from backend.core.routes import new_entity

app.include_router(new_entity.router)
```

4. **Создать тест:**

```python
# backend/tests/api/test_new_entity_api.py
def test_create_new_entity(client):
    response = client.post("/api/v1/new-entities", json={"name": "Test"})
    assert response.status_code == 201
    assert response.json()["success"] is True
```

5. **Проверить:**

```bash
pytest backend/tests/api/test_new_entity_api.py -v
curl -X POST http://localhost:8000/api/v1/new-entities -H "Content-Type: application/json" -d '{"name": "Test"}'
```

***

### Задача: Кастомизировать бизнес-логику

**Прочитать:** `CUSTOMIZATION_GUIDE.md`

**Шаги:**

1. Создать custom service в `backend/customizations/services/`
2. Наследоваться от base service из `backend/core/services/`
3. Переопределить методы
4. Зарегистрировать через DI в `backend/src/main.py`
5. Создать тест в `backend/tests/customizations/`

***

### Задача: Deployment на production

**Прочитать:** `EPLOYMENT_SEQUENCE.md`

**Команды:**

```bash
# 1. SSH в VPS
ssh root@185.177.94.29 -p 22

# 2. Перейти в проект
cd /root/mes-platform

# 3. Pull изменений
git pull origin develop

# 4. Rebuild и restart
docker compose -f docker-compose.production.yml up -d --build

# 5. Проверить health
curl https://mes-midex-ru.factoryall.ru/api/v1/health

# 6. Проверить logs
docker logs mes-backend --tail 50
```

***

## 📋 ЧЕКЛИСТ ДЛЯ КАЖДОГО ЗАПРОСА

Перед ответом пользователю проверь:

- [ ] Прочитал ли релевантную документацию из `.cursor/docs/`?
- [ ] Использовал ли MES-терминологию (ManufacturingOrder, WorkCenter, etc.)?
- [ ] Предложил ли конкретный код/команды (не абстрактные советы)?
- [ ] Добавил ли тест (если изменял бизнес-логику)?
- [ ] Указал ли команды для проверки результата?
- [ ] Структурировал ли ответ через Markdown (заголовки, таблицы)?
- [ ] Сослался ли на файлы через [file:X]?

***

## 🎯 ТЕКУЩАЯ ФАЗА ПРОЕКТА

**Фаза 1: Template Creation** ✅ ЗАВЕРШЕНА (19 января 2026, 8:46 MSK)

**Создано:**
- TEMPLATE_GUIDE.md (29 KB)
- CUSTOMIZATION_GUIDE.md (24 KB)
- README.md (секция "Using as Template")
- .template-config.yaml (метаданные)
- Ветка `template-base`
- Tag `v2.1.0-template`

**Следующая фаза:** GitHub Release Creation (в процессе)

***

## 🚨 КРИТИЧНЫЕ ОГРАНИЧЕНИЯ

1. **НЕ ИЗМЕНЯТЬ `backend/core/`** — это универсальная логика шаблона
2. **НЕ КОММИТИТЬ `.env` и `config/factory_config.yaml`**
3. **НЕ УДАЛЯТЬ ТЕСТЫ** — только добавлять/обновлять
4. **НЕ МЕНЯТЬ СТРУКТУРУ БД** без миграции Alembic
5. **НЕ ДЕПЛОИТЬ** без прохождения тестов (pytest должен быть зелёным)

***

## 📞 КОГДА ЭСКАЛИРОВАТЬ

Если задача требует:
- Архитектурных изменений (новый модуль, изменение структуры)
- Миграции БД с риском потери данных
- Изменений в production (deployment, rollback)
- Интеграции с новыми внешними системами

→ Спроси у пользователя подтверждение с детальным планом.

***

## ✅ ФИНАЛЬНАЯ ПРОВЕРКА ПЕРЕД ОТВЕТОМ

**Задай себе вопросы:**

1. Ответил ли я на вопрос пользователя конкретно?
2. Привёл ли я примеры кода/команд?
3. Сослался ли на документацию?
4. Предложил ли способ проверки результата?
5. Использовал ли MES-терминологию?

Если **ДА** на все — отправляй ответ! 🚀

***

**Версия инструкции:** 1.0  
**Последнее обновление:** 19 января 2026, 14:41 MSK  
**Автор:** AI Agent (Primary)  
**Для:** Все AI агенты Пространства "MES"

***

**Эта инструкция — единый источник истины для всех AI агентов в Пространстве. Следуй ей неукоснительно!**