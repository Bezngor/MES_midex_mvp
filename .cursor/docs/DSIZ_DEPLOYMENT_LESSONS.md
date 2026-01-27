# DSIZ Phase 2 Deployment Lessons (26.01.2026)

## 🎯 Проблемы + Фиксы

| Проблема | Причина | Фикс |
|----------|---------|------|
| `script_location = src/db/migrations` | Неправильный путь | `sed -i 's/src\/db\/migrations/backend\/src\/db/' alembic.ini` |
| Нет `env.py` | Cursor не создал | Создать с импортом DSIZ моделей |
| `src/db/migrations/` → `src/db/versions/` | Структура | `mv migrations/versions/* versions/` |
| `$DATABASE_URL=localhost` | .env не подтянулся | `postgresql://mes_user:...@db:5432/mes_production` |
| Docker пути `/app/backend/src/db/` | Dockerfile COPY | `alembic -c /app/alembic.ini` |

## 🛠️ Автоматизация Deploy (deployment.sh)

#!/bin/bash
cd /opt/mes-platform
git pull origin feat/dsiz-phase1-mrp
docker compose -f docker-compose.production.yml up -d --build

# Фикс alembic.ini
sed -i 's/script_location = src\/db/script_location = backend\/src\/db/' /app/alembic.ini

# Миграции
docker compose exec backend alembic -c /app/alembic.ini upgrade head

# Seed
docker compose exec backend psql "postgresql://mes_user:a8b2CApEA1IjXjIAJIv_Fr8w@db:5432/mes_production" -f /app/backend/src/db/seed_dsiz_data.sql

# Тест
curl -X POST https://mes-midex-ru.factoryall.ru/api/v1/dsiz/planning/run -H "Content-Type: application/json" -d '{"planning_date": "2026-01-26", "horizon_days": 7}'
🔧 Постоянный Фикс (Cursor)
text
1. backend/Dockerfile.production:
   COPY alembic.ini /app/alembic.ini
   COPY src/db /app/src/db/
   RUN sed -i 's/src\/db/backend\/src\/db/' /app/alembic.ini

2. .env.production:
   DATABASE_URL=postgresql://mes_user:...@db:5432/mes_production

3. docker-compose.production.yml:
   env_file: .env.production
   
✅ Чеклист Deploy
 git pull

 docker compose up -d --build

 alembic -c /app/alembic.ini upgrade head

 psql ... seed_dsiz_data.sql

 curl /dsiz/planning/run → success:true

