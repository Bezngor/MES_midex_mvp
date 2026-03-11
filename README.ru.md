# Шаблон MES‑платформы v2.1.0 🏭

> **Это шаблонный репозиторий.** Используйте его для создания кастомных MES‑реализаций для вашей фабрики. [github](https://github.com/Bezngor/MES_midex_mvp)

SaaS‑шаблон системы диспетчеризации производства (MES) для дискретного и процессного производства. [github](https://github.com/Bezngor/MES_midex_mvp)

## Быстрый старт

См. [docs/TEMPLATE_GUIDE.md](docs/TEMPLATE_GUIDE.md) для подробных инструкций. [github](https://github.com/Bezngor/MES_midex_mvp)

### 1. Создать проект из шаблона

Нажмите кнопку «Use this template» сверху или выполните: [github](https://github.com/Bezngor/MES_midex_mvp)

```bash
gh repo create my-factory-mes --template mes-platform-template
```

### 2. Настроить

```bash
cp config/factory_config.example.yaml config/factory_config.yaml
nano config/factory_config.yaml  
# Отредактируйте настройки
```


### 3. Задеплоить

```bash
docker compose -f docker-compose.production.yml up -d --build
```


Используемые технологии: [Python 3.11+](https://www.python.org/downloads/), [FastAPI](https://fastapi.tiangolo.com/), [React](https://react.dev/), [PostgreSQL](https://www.postgresql.org/). [github](https://github.com/Bezngor/MES_midex_mvp)

## Что входит

- ✅ **60+ API‑эндпоинтов** — Products, BOM, Batches, Inventory, MRP, Dispatching [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ **React‑дашборд** — 6 страниц [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ **Конфигурационный подход** — кастомизация на основе YAML [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ **141 модульный тест** — 93% покрытия [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ **Готово к продакшену** — Docker + SSL [github](https://github.com/Bezngor/MES_midex_mvp)

См. [docs/TEMPLATE_GUIDE.md](docs/TEMPLATE_GUIDE.md) для описания архитектуры и руководства по кастомизации. [github](https://github.com/Bezngor/MES_midex_mvp)

### Manufacturing Core (v1.0)

- ✅ Управление производственными заказами [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ Рабочие центры и планирование мощности [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ Диспетчеризация производственных задач [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ Отслеживание WIP в реальном времени [github](https://github.com/Bezngor/MES_midex_mvp)

### Material Requirements Planning (v2.0)

- ✅ Разузлование спецификаций (BOM explosion) и расчет чистой потребности [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ Округление партий для процессного производства [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ Многоуровневые спецификации (multi-level BOM) [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ Управление запасами и движениями [github](https://github.com/Bezngor/MES_midex_mvp)

### Dispatching & Scheduling (v2.1)

- ✅ Интеллектуальная диспетчеризация задач [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ Расчет загрузки рабочих центров [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ Планирование выпуска заказов [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ Управление параллельной мощностью [github](https://github.com/Bezngor/MES_midex_mvp)

### Интеграции

- ✅ n8n для автоматизации workflow [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ RESTful API (FastAPI) [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ Коннектор аналитики Power BI [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ Уведомления через webhooks [github](https://github.com/Bezngor/MES_midex_mvp)

## 📋 Стек технологий

- **Backend:** FastAPI + Python 3.11 + SQLAlchemy [github](https://github.com/Bezngor/MES_midex_mvp)
- **Frontend:** React 18 + Vite + TailwindCSS [github](https://github.com/Bezngor/MES_midex_mvp)
- **База данных:** PostgreSQL 15+ (Supabase) [github](https://github.com/Bezngor/MES_midex_mvp)
- **Автоматизация:** n8n [github](https://github.com/Bezngor/MES_midex_mvp)
- **Тестирование:** Pytest (93%+ покрытия) [github](https://github.com/Bezngor/MES_midex_mvp)
- **Деплой:** Docker + Dokploy PaaS [github](https://github.com/Bezngor/MES_midex_mvp)

## 🚀 Продакшен‑деплой

См. [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) для детальных инструкций по деплою в продакшен. [github](https://github.com/Bezngor/MES_midex_mvp)

### Быстрый старт (продакшен)

```bash
# 1. Клонировать репозиторий
git clone -b develop https://github.com/Bezngor/MES_midex.git
cd MES_midex

# 2. Настроить окружение
cp .env.example .env
nano .env
# Внести продакшен‑учетные данные

# 3. Собрать и задеплоить
docker-compose -f docker-compose.production.yml up -d --build

# 4. Применить миграции БД
docker exec mes_backend alembic upgrade head

# 5. Проверить деплой
curl https://mes-midex-ru.factoryall.ru/api/v1/health
```


Продакшен‑URL:  
Frontend — https://mes-midex-ru.factoryall.ru  
Backend API — https://mes-midex-ru.factoryall.ru/api/v1  
API Docs — https://mes-midex-ru.factoryall.ru/api/v1/docs [github](https://github.com/Bezngor/MES_midex_mvp)

***

# 🏭 Использование как шаблона для вашей фабрики

Этот репозиторий служит **универсальным MES‑шаблоном** для производственных предприятий (дискретное, процессное и гибридное производство). [github](https://github.com/Bezngor/MES_midex_mvp)

## ✨ Возможности шаблона

- ✅ **Готов к продакшену** — развернут по адресу https://mes-midex-ru.factoryall.ru [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ **Соответствие ISA‑95** — следует отраслевым стандартам MES [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ **Высокая тестируемость** — 141 тест, 93% покрытия кода [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ **Модульная архитектура** — core (универсальная логика) + config (настройки) + customizations (специфика фабрики) [github](https://github.com/Bezngor/MES_midex_mvp)
- ✅ **Готов к GitOps** — деплой на Docker + Dokploy + Traefik [github](https://github.com/Bezngor/MES_midex_mvp)

## 🚀 Быстрый старт (новая фабрика)

### 1. Клонировать шаблонную ветку

```bash
# Клонировать универсальный шаблон (без специфики конкретной фабрики)
git clone -b template-base https://github.com/Bezngor/MES_midex.git my-factory-mes
cd my-factory-mes

# Создать свою ветку разработки
git checkout -b develop
```


**Важно:** используйте ветку `template-base`, а не `main` или `develop` (в них содержится код, специфичный для конкретной фабрики). [github](https://github.com/Bezngor/MES_midex_mvp)

### 2. Настроить под вашу фабрику

```bash
# Скопировать конфигурационный шаблон
cp config/factory_config.example.yaml config/factory_config.yaml

# Отредактировать под вашу фабрику
nano config/factory_config.yaml
```


**Пример конфигурации:**

```yaml
factory:
  name: "My Factory LLC"
  location: "Moscow, Russia"
  timezone: "Europe/Moscow"

mrp:
  horizon_days: 14     # горизонт планирования (дни)
  consolidation_enabled: true  # консолидация заказов по продукту

batch_production:
  enabled: true               # поддержка пакетных процессов
  default_min_batch_kg: 500   # минимальный размер партии (кг)
  default_step_kg: 1000       # шаг размера партии (кг)

dispatching:
  strategy: "FIFO"            # стратегия диспетчеризации
  capacity_check_enabled: true # проверка мощности рабочих центров
```


### 3. Настроить окружение

```bash
# Скопировать шаблон .env
cp .env.example .env

# Отредактировать URL БД, секретный ключ, CORS‑происхождения
nano .env
```


### 4. Деплой в продакшен

```bash
# Сборка Docker‑образов
docker compose -f docker-compose.production.yml build

# Применение миграций БД
docker compose -f docker-compose.production.yml run backend alembic upgrade head

# Запуск контейнеров
docker compose -f docker-compose.production.yml up -d

# Проверка здоровья сервиса
curl https://your-domain.com/api/health
```


## 📚 Документация

- **docs/TEMPLATE_GUIDE.md** — полное руководство по использованию шаблона [github](https://github.com/Bezngor/MES_midex_mvp)
- **docs/CUSTOMIZATION_GUIDE.md** — как кастомизировать бизнес‑логику [github](https://github.com/Bezngor/MES_midex_mvp)
- **docs/DEPLOYMENT_SEQUENCE.md** — руководство по продакшен‑деплою [github](https://github.com/Bezngor/MES_midex_mvp)
- **docs/API_SPEC.md** — спецификация REST API [github](https://github.com/Bezngor/MES_midex_mvp)
- **docs/DOMAIN_MODEL.md** — доменные сущности и сервисы [github](https://github.com/Bezngor/MES_midex_mvp)

## 🏭 Поддерживаемые индустрии

- **Дискретное производство** — машиностроение, электроника, мебель [github](https://github.com/Bezngor/MES_midex_mvp)
- **Процессное производство** — косметика, химия, продукты питания и напитки [github](https://github.com/Bezngor/MES_midex_mvp)
- **Гибридное производство** — пакетные и дискретные операции вместе [github](https://github.com/Bezngor/MES_midex_mvp)

## 📦 Ключевые модули

| Модуль        | Статус       | Покрытие | Описание                                           |
|---------------|-------------|----------|----------------------------------------------------|
| MRP           | ✅ Продакшен | 95%      | Планирование потребностей в материалах             |
| Dispatching   | ✅ Продакшен | 92%      | Планирование задач и загрузки рабочих центров      |
| Inventory     | ⚠️ MVP      | 85%      | Упрощенный WMS (остатки, резервы)                  |
| BOM           | ✅ Продакшен | 90%      | Многоуровневые спецификации (Bill of Materials)    |
| Products      | ✅ Продакшен | 88%      | Нормативно‑справочная информация по продуктам      |
| Work Centers  | ✅ Продакшен | 87%      | Оборудование и управление мощностями               |
 [github](https://github.com/Bezngor/MES_midex_mvp)

## 🎓 Кейсы успеха

### DSIZ (косметическое производство)

- **Отрасль:** промышленная косметика [github](https://github.com/Bezngor/MES_midex_mvp)
- **Тип производства:** гибридное (варка партиями + дискретная фасовка) [github](https://github.com/Bezngor/MES_midex_mvp)
- **Инфраструктура:** Beget VPS (4 CPU, 8 GB RAM) [github](https://github.com/Bezngor/MES_midex_mvp)
- **URL:** https://mes-midex-ru.factoryall.ru [github](https://github.com/Bezngor/MES_midex_mvp)

**Результаты:**

- ⏱️ **Сокращение времени планирования на 60%** (автоматизация MRP) [github](https://github.com/Bezngor/MES_midex_mvp)
- 📈 **Рост загрузки оборудования на 25%** (оптимизация диспетчеризации) [github](https://github.com/Bezngor/MES_midex_mvp)
- 📉 **Снижение брака на 15%** (контроль сроков годности) [github](https://github.com/Bezngor/MES_midex_mvp)

## 🔧 Варианты кастомизации

MES‑платформа поддерживает два уровня кастомизации: [github](https://github.com/Bezngor/MES_midex_mvp)

### 1. Конфигурация (без изменения кода)

Редактируйте `config/factory_config.yaml`: [github](https://github.com/Bezngor/MES_midex_mvp)

- Горизонт планирования MRP [github](https://github.com/Bezngor/MES_midex_mvp)
- Параметры пакетного производства [github](https://github.com/Bezngor/MES_midex_mvp)
- Графики смен [github](https://github.com/Bezngor/MES_midex_mvp)
- Стратегию диспетчеризации [github](https://github.com/Bezngor/MES_midex_mvp)

### 2. Расширение бизнес‑логики

Создавайте кастомные сервисы в `backend/customizations/`: [github](https://github.com/Bezngor/MES_midex_mvp)

- Переопределение логики MRP/Dispatching через наследование [github](https://github.com/Bezngor/MES_midex_mvp)
- Добавление специфичных для фабрики бизнес‑правил [github](https://github.com/Bezngor/MES_midex_mvp)
- Интеграция с внешними системами (ERP, WMS, IoT) [github](https://github.com/Bezngor/MES_midex_mvp)

См. `docs/CUSTOMIZATION_GUIDE.md` для подробных примеров. [github](https://github.com/Bezngor/MES_midex_mvp)

## 🆘 Поддержка

- **GitHub Issues:** https://github.com/Bezngor/MES_midex/issues [github](https://github.com/Bezngor/MES_midex_mvp)
- **Discussions:** https://github.com/Bezngor/MES_midex/discussions [github](https://github.com/Bezngor/MES_midex_mvp)
- **Email:** support@your-company.com [github](https://github.com/Bezngor/MES_midex_mvp)

## 📄 Лицензия

**Проприетарная лицензия** — только для внутреннего использования.  
Распространение исходного кода третьим лицам ЗАПРЕЩЕНО без письменного согласия. [github](https://github.com/Bezngor/MES_midex_mvp)

***

## 🛠️ Среда разработки

### Предварительные требования

Python 3.11+, Node.js 18+, PostgreSQL 15+, Docker & Docker Compose. [github](https://github.com/Bezngor/MES_midex_mvp)

### Локальная разработка (через Docker)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/Bezngor/MES_midex.git
cd MES_midex

# 2. Запустить dev‑окружение
docker-compose up -d
```


```text
# 3. Доступ к сервисам
- Frontend:  http://localhost:3000
- Backend API: http://localhost:8000
- API Docs:  http://localhost:8000/docs
```


### Ручная настройка (без Docker)

**Backend:**

```bash
cd backend
pip install poetry
poetry install
poetry run alembic upgrade head
poetry run uvicorn backend.src.main:app --reload
```


**Frontend:**

```bash
cd frontend
npm install
npm run dev
```


### 🧪 Тестирование

```bash
cd backend
poetry run pytest
# или с покрытием
poetry run pytest --cov=backend/src --cov-report=html
```


Покрытие тестами: 93%+ (141 тест проходит). [github](https://github.com/Bezngor/MES_midex_mvp)

См. `docs/TESTING.md` для подробного руководства по тестированию. [github](https://github.com/Bezngor/MES_midex_mvp)

***

## 📚 Дополнительная документация

Архитектура и дизайн: [github](https://github.com/Bezngor/MES_midex_mvp)

- Системная архитектура [github](https://github.com/Bezngor/MES_midex_mvp)
- Домейн‑модель [github](https://github.com/Bezngor/MES_midex_mvp)
- Схема БД [github](https://github.com/Bezngor/MES_midex_mvp)
- Спецификация API [github](https://github.com/Bezngor/MES_midex_mvp)

Модули: [github](https://github.com/Bezngor/MES_midex_mvp)

- Руководство по MRP [github](https://github.com/Bezngor/MES_midex_mvp)
- Руководство по Dispatching [github](https://github.com/Bezngor/MES_midex_mvp)
- Руководство по n8n‑workflow [github](https://github.com/Bezngor/MES_midex_mvp)

Деплой и эксплуатация: [github](https://github.com/Bezngor/MES_midex_mvp)

- Продакшен‑деплой [github](https://github.com/Bezngor/MES_midex_mvp)
- Docker‑архитектура для продакшена [github](https://github.com/Bezngor/MES_midex_mvp)
- Руководство по тестированию [github](https://github.com/Bezngor/MES_midex_mvp)

***

## 🗂️ Структура проекта

```text
mes-platform/
├── backend/                  # FastAPI backend
│   ├── src/                  # Исходный код
│   ├── tests/                # Тесты Pytest
│   ├── alembic/              # Миграции БД
│   └── Dockerfile.production
├── frontend/                 # React frontend
│   ├── src/
│   ├── Dockerfile.production
│   └── nginx.conf
├── .cursor/docs/             # Документы для AI-контекста
├── docs/                     # Публичная документация
├── docker-compose.yml        # Dev‑окружение
├── docker-compose.production.yml # Продакшен
└── .env.example
```


См. `docs/REPOSITORY_STRUCTURE.md` для подробного описания структуры репозитория. [github](https://github.com/Bezngor/MES_midex_mvp)

***

## 📊 API‑эндпоинты

### Manufacturing Orders

- `POST /api/v1/orders` — создать производственный заказ [github](https://github.com/Bezngor/MES_midex_mvp)
- `GET /api/v1/orders` — список заказов [github](https://github.com/Bezngor/MES_midex_mvp)
- `GET /api/v1/orders/{id}` — детали заказа [github](https://github.com/Bezngor/MES_midex_mvp)
- `PATCH /api/v1/orders/{id}` — обновление статуса заказа [github](https://github.com/Bezngor/MES_midex_mvp)

### MRP (Material Requirements Planning)

- `POST /api/v1/mrp/run` — запуск расчета MRP [github](https://github.com/Bezngor/MES_midex_mvp)
- `GET /api/v1/batches` — список производственных партий [github](https://github.com/Bezngor/MES_midex_mvp)
- `GET /api/v1/inventory` — уровни запасов [github](https://github.com/Bezngor/MES_midex_mvp)

### Dispatching

- `POST /api/v1/dispatching/release-orders` — выпуск заказов в производство [github](https://github.com/Bezngor/MES_midex_mvp)
- `POST /api/v1/dispatching/dispatch-tasks` — диспетчеризация задач по рабочим центрам [github](https://github.com/Bezngor/MES_midex_mvp)
- `GET /api/v1/dispatching/work-center-load` — загрузка рабочих центров [github](https://github.com/Bezngor/MES_midex_mvp)

Полная документация API: `http://localhost:8000/docs` (Swagger UI). [github](https://github.com/Bezngor/MES_midex_mvp)

***

## 🔐 Переменные окружения

См. `.env.example` для списка переменных: [github](https://github.com/Bezngor/MES_midex_mvp)

- `DATABASE_URL` — строка подключения к PostgreSQL [github](https://github.com/Bezngor/MES_midex_mvp)
- `SECRET_KEY` — секрет JWT (сгенерировать: `openssl rand -hex 32`) [github](https://github.com/Bezngor/MES_midex_mvp)
- `CORS_ORIGINS` — разрешенные origins для CORS [github](https://github.com/Bezngor/MES_midex_mvp)
- `ENVIRONMENT` — `development` или `production` [github](https://github.com/Bezngor/MES_midex_mvp)

***

## 🤝 Вклад

1. Форкните репозиторий. [github](https://github.com/Bezngor/MES_midex_mvp)
2. Создайте ветку фичи (`git checkout -b feature/amazing-feature`). [github](https://github.com/Bezngor/MES_midex_mvp)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`). [github](https://github.com/Bezngor/MES_midex_mvp)
4. Запушьте ветку (`git push origin feature/amazing-feature`). [github](https://github.com/Bezngor/MES_midex_mvp)
5. Откройте Pull Request. [github](https://github.com/Bezngor/MES_midex_mvp)

***

## 📝 Changelog

См. `CHANGELOG.md` для истории версий. [github](https://github.com/Bezngor/MES_midex_mvp)

Последний релиз: **v2.1.0** [github](https://github.com/Bezngor/MES_midex_mvp)

- ✨ Добавлен `DispatchingService` с выпуском заказов и диспетчеризацией задач. [github](https://github.com/Bezngor/MES_midex_mvp)
- ✨ Расчет загрузки рабочих центров с учетом параллельной мощности. [github](https://github.com/Bezngor/MES_midex_mvp)
- ✨ Конфигурация продакшен‑деплоя (Docker, nginx, Dokploy). [github](https://github.com/Bezngor/MES_midex_mvp)
- 📚 Полная документация по деплою. [github](https://github.com/Bezngor/MES_midex_mvp)
- 🧪 90%+ покрытия тестами для модуля диспетчеризации. [github](https://github.com/Bezngor/MES_midex_mvp)

***

## 📄 Лицензия

Этот проект — проприетарное ПО. Все права защищены. [github](https://github.com/Bezngor/MES_midex_mvp)

***

## 👥 Авторы

- Bezngor — первоначальная разработка. [github](https://github.com/Bezngor/MES_midex_mvp)

**Production URL:** https://mes-midex-ru.factoryall.ru  
**API Docs:** https://mes-midex-ru.factoryall.ru/api/v1/docs [github](https://github.com/Bezngor/MES_midex_mvp)

***
