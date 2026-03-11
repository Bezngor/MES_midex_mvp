# MES_midex MVP 🏭

> **MVP демонстрация MES-системы** для производственного планирования. Стратегическое и тактическое планирование производства.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Описание

**MES_midex** — система управления производственными операциями (MES) для предприятий лёгкой промышленности.

### Основные возможности MVP:

- ✅ **Стратегическое планирование** — автоматический расчёт производственного плана на недели/месяцы
- ✅ **Тактическое планирование** — корректировка плана «на лету» с учётом Frozen Zone
- ✅ **Изменения заказов** — автоматическое выявление новых/изменённых заказов
- ✅ **Визуализация** — Гантт-диаграммы загрузки оборудования
- ✅ **MRP-расчёт** — Material Requirements Planning с консолидацией по изделиям
- ✅ **DSIZ-фреймворк** — кастомизация под специфику предприятия

---

## 🎯 Для кого

| Роль | Задачи в системе |
|------|------------------|
| **Производственный директор** | Стратегическое планирование, контроль загрузки цехов |
| **Мастер цеха** | Суточное планирование, корректировка заданий, учёт брака |
| **Планировщик** | Формирование и оптимизация производственного плана |
| **Менеджер заказов** | Контроль поступления заказов, согласование сроков |

---

## 🚀 Быстрый старт

### Требования

- Docker & Docker Compose
- PostgreSQL 15+ (или Supabase)
- Node.js 18+ (для разработки фронтенда)
- Python 3.11+ (для разработки бэкенда)

### Установка и запуск

```bash
# 1. Клонирование репозитория
git clone https://github.com/Bezngor/MES_midex_mvp.git
cd MES_midex_mvp

# 2. Настройка окружения
cp .env.example .env
# Отредактируйте .env — укажите DATABASE_URL и SECRET_KEY

# 3. Запуск в Docker
docker-compose -f docker-compose.production.yml up -d --build

# 4. Применение миграций
docker exec mes_backend alembic upgrade head

# 5. Проверка
curl http://localhost:8000/api/v1/health
```

### URL после запуска

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/v1
- **API Docs (Swagger)**: http://localhost:8000/api/v1/docs

---

## 🏗️ Архитектура

```
MES_midex/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── api/            # API endpoints
│   │   ├── services/       # Business logic (MRP, Dispatching, Planning)
│   │   ├── models/         # SQLAlchemy models
│   │   └── core/           # Config, security, dependencies
│   ├── tests/              # Pytest tests (92%+ coverage)
│   └── alembic/            # Database migrations
├── frontend/               # React + TypeScript
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Page components
│   │   └── stores/         # State management (Zustand)
│   └── tests/
├── .cursor/docs/           # AI context & documentation
└── docker-compose.yml      # Docker orchestration
```

---

## 💻 Технологический стек

### Backend
- **Framework**: FastAPI (async Python)
- **ORM**: SQLAlchemy 2.0 + Alembic
- **Database**: PostgreSQL 15+ (Supabase)
- **Auth**: JWT (FastAPI-users)
- **Validation**: Pydantic v2
- **Testing**: Pytest + pytest-asyncio (92%+ coverage)

### Frontend
- **Framework**: React 18
- **Language**: TypeScript (strict mode)
- **Build**: Vite
- **Styling**: TailwindCSS + Ant Design
- **State**: Zustand
- **Query**: TanStack Query

### DevOps
- **Container**: Docker + Docker Compose
- **Deployment**: Dokploy PaaS
- **CI/CD**: GitHub Actions (опционально)

### Интеграции
- **Workflow**: n8n
- **External**: 1C API (в разработке)

---

## 📊 API Endpoints

### Стратегическое планирование

```http
POST   /api/v1/strategy/plan/recalculate     # Пересчёт плана
GET    /api/v1/strategy/plan                   # Получить текущий план
GET    /api/v1/strategy/gantt                  # Данные для Гантта
```

### Изменения заказов

```http
GET    /api/v1/orders/changes                  # Список изменений
POST   /api/v1/orders/{id}/approve              # Утвердить изменение
POST   /api/v1/orders/{id}/reject               # Отклонить изменение
```

### Загрузка данных

```http
POST   /api/v1/import/csv                       # Загрузка заказов из CSV
POST   /api/v1/import/excel                   # Загрузка заказов из Excel
```

### Справочники

```http
GET    /api/v1/products                        # Список изделий
GET    /api/v1/work-centers                    # Рабочие центры
GET    /api/v1/bom/{product_id}                # Технологическая карта
```

Полная документация API: `/api/v1/docs` (Swagger UI)

---

## 🧪 Тестирование

### Backend

```bash
cd backend
pip install poetry
poetry install
poetry run pytest

# С coverage
poetry run pytest --cov=backend/src --cov-report=html
```

**Покрытие тестами**: 92%+ (140+ тестов)

### Frontend

```bash
cd frontend
npm install
npm run test
```

---

## 📖 Документация

- [TECHNICAL_SPECIFICATION.md](./TECHNICAL_SPECIFICATION.md) — Техническое задание
- [.cursor/docs/](./.cursor/docs/) — Полная документация проекта
  - [BUSINESS_PROCESS_REFERENCE.md](./.cursor/docs/02_architecture/business-process-reference.md) — Бизнес-процессы
  - [STRATEGIC_ALGORITHM.md](./.cursor/docs/02_architecture/STRATEGIC_ALGORITHM.md) — Алгоритм планирования
  - [STRATEGY_TAB_UX_AND_FROZEN_ZONE.md](./.cursor/docs/STRATEGY_TAB_UX_AND_FROZEN_ZONE.md) — UX + Frozen Zone

---

## 🛣️ Roadmap

| Этап | Статус | Описание |
|------|--------|----------|
| **MVP** | 🚧 В работе | Стратегическое планирование, загрузка CSV/Excel |
| **Phase B** | 📋 Запланирован | Тактическое планирование, Frozen Zone |
| **Phase C** | 💡 Идея | Интеграция 1С, real-time обновления |
| **Phase D** | 💡 Идея | AI/ML прогнозирование загрузки |

---

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку: `git checkout -b feature/amazing-feature`
3. Закоммитьте изменения: `git commit -m 'Add amazing feature'`
4. Запушьте: `git push origin feature/amazing-feature`
5. Откройте Pull Request

---

## 📝 Лицензия

Этот проект распространяется под лицензией **MIT**.

См. файл [LICENSE](./LICENSE) для подробностей.

---

## 👥 Команда

- **Идея и разработка**: Владимир ([@ProbaloMas](https://t.me/ProbaloMas))
- **Project Manager**: Q (OpenClaw Agent)
- **Код**: Cursor AI + Human-in-the-loop

---

## 📬 Контакты

- GitHub Issues: [github.com/Bezngor/MES_midex_mvp/issues](https://github.com/Bezngor/MES_midex_mvp/issues)
- Telegram: [@ProbaloMas](https://t.me/ProbaloMas)

---

<p align="center">
  <b>MES_midex MVP</b> — автоматизация планирования производства
</p>
