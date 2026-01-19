# 🚀 Production Deployment Sequence Guide

**Версия:** 1.0  
**Дата:** 19 января 2026  
**Статус:** Проверено на Beget VPS

Этот документ описывает **ПРАВИЛЬНУЮ последовательность** развёртывания MES Platform v2.1.0 в production. Следование этому порядку позволит избежать ошибок и потери времени.

---

## ⚠️ КРИТИЧЕСКИЕ ПРАВИЛА

### 1. Проверка портов ПЕРЕД запуском

# Всегда проверяйте занятые порты перед docker compose up
netstat -tulpn | grep -E ":8000|:8002|:3000|:3002"

# Если порты заняты - измените их в docker-compose.production.yml
2. GitOps подход ОБЯЗАТЕЛЕН
❌ НИКОГДА не редактируйте файлы напрямую на сервере через nano

✅ ВСЕГДА изменения через Cursor → commit → push → pull на сервере

3. Откат при проблемах
Если что-то сломалось - откатывайтесь к последнему рабочему коммиту через git reset --hard

Не пытайтесь чинить "на лету" на сервере

📋 Pre-Deployment Checklist
Шаг 0: Подготовка окружения (одноразово)
Проверить что установлено на VPS:

bash
docker --version    # Должен быть Docker 24.0+
docker compose version  # Должен быть Compose v2
Проверить что Supabase развёрнут:

bash
docker ps | grep supabase
# Должны быть контейнеры: supabase-db, supabase-kong, supabase-rest, supabase-studio
Узнать имя сети Supabase:

bash
docker network ls | grep supabase
# Пример: main-supabase-1kebyl
Узнать имя контейнера PostgreSQL:

bash
docker ps | grep supabase | grep db
# Пример: main-supabase-1kebyl-supabase-db
Получить пароль PostgreSQL из Dokploy UI:

Dokploy → Supabase → Environment Variables → POSTGRES_PASSWORD

Сохраните пароль в безопасном месте

🎯 Deployment Sequence (Первичное развёртывание)
Phase 1: Клонирование репозитория
bash
# 1. SSH на VPS
ssh root@YOUR_VPS_IP

# 2. Перейти в рабочую директорию
cd /opt

# 3. Клонировать репозиторий
git clone https://github.com/Bezngor/MES_midex.git mes-platform
cd mes-platform

# 4. Переключиться на ветку develop
git checkout develop

# 5. Проверить последний коммит
git log --oneline -1
Phase 2: Конфигурация окружения
bash
# 1. Создать .env файл
nano .env
Содержимое .env:

text
# Database (используйте данные из Pre-Deployment Checklist)
DATABASE_URL=postgresql://postgres:ВАШ_ПАРОЛЬ@main-supabase-1kebyl-supabase-db:5432/postgres

# Backend
SECRET_KEY=ГЕНЕРИРУЙТЕ_ЧЕРЕЗ_openssl_rand_-hex_32
ENVIRONMENT=production

# CORS (замените на ваш домен)
CORS_ORIGINS=https://mes-midex-ru.factoryall.ru,https://api.mes-midex-ru.factoryall.ru
Генерация SECRET_KEY:

bash
openssl rand -hex 32
bash
# 2. Сохранить и выйти из nano
# Ctrl+O -> Enter -> Ctrl+X
Phase 3: Проверка конфигурации docker-compose
bash
# 1. Проверить занятые порты
netstat -tulpn | grep -E ":8000|:3000"

# 2. Если порты 8000/3000 заняты - используйте 8002/3002
# Отредактируйте через GitOps (см. ниже)
Если нужно изменить порты:

В Cursor (на компе):
Открыть docker-compose.production.yml

Изменить:

text
backend:
  ports:
    - "8002:8000"  # Вместо 8000:8000

frontend:
  ports:
    - "3002:80"    # Вместо 3000:80
Commit: git commit -am "fix: change ports to 8002/3002"

Push: git push origin develop

На сервере (Termius):
bash
cd /opt/mes-platform
git pull origin develop
Phase 4: Проверка Docker сетей
bash
# 1. Проверить что backend в обеих сетях
cat docker-compose.production.yml | grep -A 20 "backend:" | grep -A 5 "networks:"

# Должно быть:
# networks:
#   - dokploy-network
#   - main-supabase-1kebyl  # ← Имя вашей сети Supabase
Если сети нет - добавьте через GitOps:

В Cursor:
text
services:
  backend:
    networks:
      - dokploy-network
      - main-supabase-1kebyl  # Замените на ваше имя сети

networks:
  dokploy-network:
    external: true
  main-supabase-1kebyl:
    external: true
Phase 5: Build и запуск контейнеров
bash
# 1. Перейти в директорию проекта
cd /opt/mes-platform

# 2. Build образов
docker compose -f docker-compose.production.yml build

# Ожидаемое время: 50-60 секунд

# 3. Запустить контейнеры
docker compose -f docker-compose.production.yml up -d

# 4. Подождать healthcheck (45 секунд)
sleep 45

# 5. Проверить статус
docker compose -f docker-compose.production.yml ps
Ожидаемый вывод шага 5:

text
NAME           STATUS
mes_backend    Up (healthy)
mes_frontend   Up (healthy)
Phase 6: Применение миграций БД
bash
# 1. Проверить текущее состояние БД
docker exec mes_backend sh -c 'psql $DATABASE_URL -c "\dt"'

# Если таблиц нет - применить миграции:

# 2. Применить миграции
docker exec mes_backend alembic upgrade head

# Ожидаемый вывод:
# INFO  [alembic.runtime.migration] Running upgrade  -> 20240101000000, initial_schema
# INFO  [alembic.runtime.migration] Running upgrade 20240101000000 -> 20260114000001, add_process_manufacturing_models
# INFO  [alembic.runtime.migration] Running upgrade 20260114000001 -> 20260114000002, add_ship_in_work_to_orderstatus

# 3. Проверить что таблицы созданы (должно быть 13 таблиц)
docker exec mes_backend sh -c 'psql $DATABASE_URL -c "\dt"'
Phase 7: Проверка работоспособности
bash
# 1. Health endpoint (локально, используйте ваш порт)
curl http://localhost:8002/api/v1/health

# Ожидаемый ответ:
# {"status":"healthy","version":"2.1.0","environment":"production","database":"connected"}

# 2. Frontend (локально, используйте ваш порт)
curl -I http://localhost:3002/

# Ожидаемый ответ:
# HTTP/1.1 200 OK

# 3. HTTPS через домен
curl https://mes-midex-ru.factoryall.ru/api/v1/health

# Ожидаемый ответ:
# {"status":"healthy","version":"2.1.0","environment":"production","database":"connected"}

# 4. Проверить логи (не должно быть ERROR)
docker compose -f docker-compose.production.yml logs backend | tail -50
docker compose -f docker-compose.production.yml logs frontend | tail -20
🔄 Update Sequence (Обновление существующего деплоя)
Стандартное обновление (без изменений БД)
bash
# 1. SSH на VPS
cd /opt/mes-platform

# 2. Получить изменения
git pull origin develop

# 3. Rebuild и перезапуск
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d

# 4. Проверка
sleep 45
curl http://localhost:8002/api/v1/health
Обновление с миграциями БД
bash
# 1-2. То же что выше

# 3. Применить миграции
docker exec mes_backend alembic upgrade head

# 4. Перезапуск
docker compose -f docker-compose.production.yml restart backend frontend

# 5. Проверка
sleep 30
curl http://localhost:8002/api/v1/health
🚨 Troubleshooting: Типичные проблемы
Проблема 1: Backend не стартует (unhealthy)
Диагностика:

bash
# 1. Проверить логи
docker logs mes_backend --tail 50

# 2. Проверить DATABASE_URL
docker exec mes_backend env | grep DATABASE_URL

# 3. Проверить подключение к БД
docker exec mes_backend sh -c 'psql $DATABASE_URL -c "SELECT version();"'
Возможные причины:

❌ Неправильный DATABASE_URL в .env

❌ Backend не в сети Supabase

❌ Неправильное имя контейнера PostgreSQL

Решение: См. PRODUCTION_CONNECTIVITY_GUIDE.md

Проблема 2: Порты заняты
Ошибка:

text
Bind for :::8000 failed: port is already allocated
Диагностика:

bash
# Найти что занимает порт
docker ps | grep -E "8000|3000"
netstat -tulpn | grep -E ":8000|:3000"
Решение:

Измените порты в docker-compose.production.yml через GitOps

Используйте 8002/3002 вместо 8000/3000

Проблема 3: Frontend показывает 502 Bad Gateway
Причина: Nginx закэшировал старый IP backend после docker compose up -d --force-recreate.

Решение:

bash
# Всегда перезапускайте frontend после пересоздания backend
docker compose -f docker-compose.production.yml restart frontend
Проблема 4: "Всё сломалось, как откатиться?"
Решение:

bash
# 1. Посмотреть историю коммитов
git log --pretty=format:"%h - %ad : %s" --date=format:"%Y-%m-%d %H:%M" --since="3 days ago"

# 2. Найти последний рабочий коммит (например f0f7881)

# 3. Откатиться
git reset --hard f0f7881

# 4. Перезапустить
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml up -d

# 5. Проверка
sleep 45
curl http://localhost:8002/api/v1/health
✅ Production Readiness Checklist
После успешного деплоя проверьте:

 Backend health endpoint возвращает "database":"connected"

 Frontend доступен через HTTPS домен

 HTTP → HTTPS редирект работает (308 Permanent Redirect)

 SSL сертификат Let's Encrypt активен

 Миграции БД применены (13 таблиц)

 API endpoints доступны через /api/v1/

 Swagger UI доступен на /api/docs (или ReDoc на /api/redoc)

 В логах нет ERROR или CRITICAL сообщений

 Backend в двух сетях: dokploy-network + main-supabase-1kebyl

 Frontend в сети dokploy-network

📚 Связанные документы
PRODUCTION_CONNECTIVITY_GUIDE.md - Детальное руководство по подключениям

DOCKER_PRODUCTION.md - Docker архитектура

DEPLOYMENT.md - Общее руководство по деплою

DATABASE_SCHEMA.md - Схема БД и миграции

🎯 Резюме: Ключевые принципы
Проверяйте порты перед запуском

Используйте GitOps для всех изменений

Откатывайтесь при проблемах вместо починки "на лету"

Перезапускайте frontend после изменений backend

Следуйте последовательности из этого документа

При возникновении проблем:

Проверьте Troubleshooting секцию

Посмотрите логи контейнеров

Откатитесь к последнему рабочему коммиту

Если не помогло - создайте issue в GitHub