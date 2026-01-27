# PRODUCTION_CONNECTIVITY_GUIDE.md

```markdown
# Production Connectivity Guide: Frontend, Backend, Database

**Версия:** 1.0  
**Дата:** 18 января 2026  
**Автор:** Production Deployment Team  

Этот документ содержит подробные инструкции по подключению frontend, backend и базы данных в production окружении на Beget VPS с Dokploy. Включает все грабли и их решения из реального деплоя.

---

## 🎯 Целевая архитектура

```
Internet (HTTPS)
    ↓
Traefik (dokploy-network)
    ↓
Frontend nginx (dokploy-network)
    ↓
Backend FastAPI (dokploy-network + main-supabase-1kebyl)
    ↓
Supabase PostgreSQL (main-supabase-1kebyl)
```

---

## 📋 Предварительные требования

### Что должно быть развёрнуто:
- ✅ Beget VPS с Docker и Dokploy
- ✅ Supabase в Dokploy (создаёт сеть `main-supabase-1kebyl`)
- ✅ Домен настроен (A-record → IP сервера)
- ✅ Traefik работает в `dokploy-network`

### Информация которую нужно собрать:

```bash
# 1. Найти имя сети Supabase
docker network ls | grep supabase
# Пример вывода: main-supabase-1kebyl

# 2. Найти имя контейнера PostgreSQL
docker ps | grep supabase | grep db
# Пример вывода: main-supabase-1kebyl-supabase-db

# 3. Найти имя сети Dokploy
docker network ls | grep dokploy
# Обычно: dokploy-network

# 4. Получить DATABASE_URL из Supabase
# В Dokploy UI → Supabase → Environment Variables → POSTGRES_PASSWORD
# Формат: postgresql://postgres:PASSWORD@CONTAINER_NAME:5432/postgres
```

---

## 🔧 Phase 1: Настройка Backend подключения к БД

### Проблема #1: Backend не видит Supabase (DNS resolution failed)

**Симптом:**
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "error": "could not translate host name \"supabase-db\" to address"
}
```

**Причина:** Backend и Supabase в разных Docker сетях.

**Решение:**

#### Шаг 1.1: Добавить сеть в docker-compose.production.yml

```yaml
services:
  backend:
    # ... остальная конфигурация ...
    networks:
      - dokploy-network       # Для связи с frontend/Traefik
      - main-supabase-1kebyl  # Для связи с PostgreSQL
    env_file:
      - .env

networks:
  dokploy-network:
    external: true
  main-supabase-1kebyl:
    external: true
```

#### Шаг 1.2: Настроить DATABASE_URL в .env

**ВАЖНО:** Используйте **имя контейнера** Supabase, а не `localhost` или `supabase-db`.

```bash
# В файле .env на сервере
DATABASE_URL=postgresql://postgres:ВАЫШ_ПАРОЛЬ@main-supabase-1kebyl-supabase-db:5432/postgres

# ⚠️ НЕПРАВИЛЬНО:
# DATABASE_URL=postgresql://postgres:PASSWORD@localhost:5432/postgres
# DATABASE_URL=postgresql://postgres:PASSWORD@supabase-db:5432/postgres
```

**Как узнать правильное имя контейнера:**
```bash
docker ps | grep supabase | grep db
# Скопируйте имя контейнера из вывода
```

#### Шаг 1.3: Проверка подключения

```bash
# Применить изменения
cd /opt/mes-platform
docker compose -f docker-compose.production.yml up -d backend

# Подождать healthcheck
sleep 45

# Проверить сети контейнера (должно быть ДВЕ сети)
docker inspect mes_backend --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}'
# Ожидаемый вывод: dokploy-network main-supabase-1kebyl

# Проверить подключение к БД
curl http://localhost:8002/api/v1/health
# Ожидаемый вывод: {"status":"healthy","database":"connected"}
```

---

## 🔧 Phase 2: Настройка Frontend → Backend проксирования

### Проблема #2: Frontend получает 502 Bad Gateway от backend

**Симптом:**
```bash
curl https://mes-midex-ru.factoryall.ru/api/v1/health
# HTTP/2 502
```

**Nginx логи:**
```
connect() failed (113: Host is unreachable) while connecting to upstream
upstream: "http://10.0.1.23:8000/api/v1/health"
```

**Причина:** Nginx закэшировал старый IP адрес backend контейнера после `docker compose up -d --force-recreate`.

**Решение:**

#### Шаг 2.1: Всегда перезапускайте frontend после изменений backend

```bash
# ❌ НЕПРАВИЛЬНО:
docker compose -f docker-compose.production.yml up -d --force-recreate backend
# Frontend продолжает обращаться к старому IP

# ✅ ПРАВИЛЬНО:
docker compose -f docker-compose.production.yml up -d --force-recreate backend
docker compose -f docker-compose.production.yml restart frontend
# Или пересоздать оба сразу:
docker compose -f docker-compose.production.yml up -d
```

#### Шаг 2.2: Проверка nginx конфигурации

```bash
# Проверить что nginx правильно настроен на проксирование
docker exec mes_frontend cat /etc/nginx/conf.d/default.conf

# Должно быть:
# location /api/ {
#     proxy_pass http://mes_backend:8000;  # ← Имя контейнера, порт 8000 (внутренний)
#     ...
# }
```

**ВАЖНО:** В nginx используется **внутренний порт контейнера** (8000), а не внешний (8002).

#### Шаг 2.3: Проверка связности

```bash
# Проверить что frontend видит backend в сети
docker exec mes_frontend ping -c 2 mes_backend
# Должен вернуть: 64 bytes from mes_backend (10.0.x.x): icmp_seq=1 ttl=64

# Проверить API изнутри frontend контейнера
docker exec mes_frontend wget -qO- http://mes_backend:8000/api/v1/health
# Должен вернуть: {"status":"healthy","database":"connected"}

# Если всё OK, проверить через HTTPS
curl https://mes-midex-ru.factoryall.ru/api/v1/health
```

---

## 🔧 Phase 3: Настройка Traefik HTTPS маршрутизации

### Проблема #3: Frontend не доступен через домен

**Симптом:**
```bash
curl https://mes-midex-ru.factoryall.ru/
# curl: (6) Could not resolve host
```

**Причина:** Traefik не настроен для маршрутизации трафика на frontend.

**Решение:**

#### Шаг 3.1: Добавить Traefik labels в docker-compose.production.yml

```yaml
services:
  frontend:
    # ... остальная конфигурация ...
    networks:
      - dokploy-network
    labels:
      # HTTPS router
      - "traefik.enable=true"
      - "traefik.http.routers.mes-frontend.rule=Host(`mes-midex-ru.factoryall.ru`)"
      - "traefik.http.routers.mes-frontend.entrypoints=websecure"
      - "traefik.http.routers.mes-frontend.tls=true"
      - "traefik.http.routers.mes-frontend.tls.certresolver=letsencrypt"
      - "traefik.http.services.mes-frontend.loadbalancer.server.port=80"
      
      # HTTP router с редиректом на HTTPS
      - "traefik.http.routers.mes-frontend-http.rule=Host(`mes-midex-ru.factoryall.ru`)"
      - "traefik.http.routers.mes-frontend-http.entrypoints=web"
      - "traefik.http.routers.mes-frontend-http.middlewares=redirect-to-https@file"
```

**Пояснения:**
- `websecure` = HTTPS entrypoint (порт 443)
- `web` = HTTP entrypoint (порт 80)
- `redirect-to-https@file` = middleware из Dokploy для редиректа HTTP → HTTPS
- `loadbalancer.server.port=80` = внутренний порт nginx контейнера

#### Шаг 3.2: Применить и проверить

```bash
# Применить изменения
docker compose -f docker-compose.production.yml up -d frontend

# Подождать 30 секунд (генерация SSL сертификата)
sleep 30

# Проверить что Traefik видит frontend
docker exec dokploy-traefik wget -qO- http://127.0.0.1:8080/api/http/routers 2>/dev/null | grep mes-frontend
# Должно показать два роутера: mes-frontend (HTTPS) и mes-frontend-http (HTTP)

# Проверить HTTP → HTTPS редирект
curl -I http://mes-midex-ru.factoryall.ru/
# Ожидаемый вывод: HTTP/1.1 308 Permanent Redirect
#                   Location: https://mes-midex-ru.factoryall.ru/

# Проверить HTTPS доступ
curl -I https://mes-midex-ru.factoryall.ru/
# Ожидаемый вывод: HTTP/2 200
```

---

## 🔧 Phase 4: Применение миграций БД

### Проблема #4: Alembic не находит миграции в Docker

**Симптом:**
```bash
docker exec mes_backend alembic current
# ERROR [alembic.util.messaging] Can't locate revision identified by '...'
```

**Причина:** Неправильные пути к миграциям в Dockerfile или alembic.ini.

**Решение:**

#### Шаг 4.1: Правильная структура Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Копировать alembic.ini в корень /app
COPY alembic.ini ./alembic.ini

# Копировать исходники в /app/backend/src/
COPY src/ ./backend/src/

# Миграции должны быть в /app/backend/src/alembic/
# (проверьте что они там есть)
```

#### Шаг 4.2: Правильная конфигурация alembic.ini

```ini
[alembic]
# Путь к миграциям относительно /app
script_location = backend/src/alembic

# Путь к env.py относительно script_location
# Итоговый путь: /app/backend/src/alembic/env.py

[loggers]
keys = root,sqlalchemy,alembic
```

#### Шаг 4.3: Применение миграций

```bash
# Пересоздать backend с исправленным Dockerfile
docker compose -f docker-compose.production.yml build backend
docker compose -f docker-compose.production.yml up -d backend

# Подождать запуска
sleep 45

# Проверить текущую версию БД
docker exec mes_backend alembic current
# Должен показать: (head) если миграций нет

# Применить миграции
docker exec mes_backend alembic upgrade head
# Должен показать:
# INFO  [alembic.runtime.migration] Running upgrade  -> 20240101000000, initial_schema
# INFO  [alembic.runtime.migration] Running upgrade 20240101000000 -> 20260114000001, ...

# Проверить что таблицы созданы
docker exec mes_backend sh -c 'psql $DATABASE_URL -c "\dt"'
# Должен показать список таблиц (13 таблиц)
```

---

## 🛠️ Troubleshooting: Типичные проблемы

### Backend не запускается (unhealthy)

```bash
# 1. Проверить логи
docker logs mes_backend --tail 50

# 2. Проверить DATABASE_URL
docker exec mes_backend env | grep DATABASE_URL

# 3. Проверить подключение к БД вручную
docker exec mes_backend sh -c 'psql $DATABASE_URL -c "SELECT version();"'
```

### Frontend показывает 502 Bad Gateway

```bash
# 1. Проверить что backend здоров
docker ps | grep mes_backend
# Должно быть: Up X minutes (healthy)

# 2. Проверить логи nginx
docker logs mes_frontend --tail 30

# 3. Проверить IP адреса контейнеров
docker inspect mes_backend | grep IPAddress
docker inspect mes_frontend | grep IPAddress

# 4. Перезапустить frontend (обновить DNS кэш)
docker compose -f docker-compose.production.yml restart frontend
```

### Traefik не маршрутизирует на frontend

```bash
# 1. Проверить что frontend в сети dokploy-network
docker network inspect dokploy-network --format '{{range .Containers}}{{.Name}} {{end}}' | grep mes_frontend

# 2. Проверить Traefik labels
docker inspect mes_frontend | grep -A 10 Labels | grep traefik

# 3. Проверить роутеры Traefik
docker exec dokploy-traefik wget -qO- http://127.0.0.1:8080/api/http/routers 2>/dev/null | grep mes-frontend

# 4. Проверить логи Traefik
docker logs dokploy-traefik --tail 50 | grep mes
```

### Миграции не применяются

```bash
# 1. Проверить структуру файлов в контейнере
docker exec mes_backend ls -la /app/
docker exec mes_backend ls -la /app/backend/src/alembic/

# 2. Проверить alembic.ini
docker exec mes_backend cat /app/alembic.ini | grep script_location

# 3. Попробовать запустить alembic вручную
docker exec mes_backend alembic revision --autogenerate -m "test"
```

---

## 📊 Checklist: Проверка корректности подключений

### Backend → Database
- [ ] Backend в сети `main-supabase-1kebyl`
- [ ] DATABASE_URL указывает на правильное имя контейнера PostgreSQL
- [ ] `curl http://localhost:8002/api/v1/health` возвращает `"database":"connected"`
- [ ] Миграции Alembic применены успешно

### Frontend → Backend
- [ ] Frontend в сети `dokploy-network`
- [ ] Backend в сети `dokploy-network`
- [ ] `docker exec mes_frontend ping mes_backend` работает
- [ ] `docker exec mes_frontend wget http://mes_backend:8000/api/v1/health` работает
- [ ] Nginx конфигурация проксирует на `http://mes_backend:8000`

### Traefik → Frontend
- [ ] Frontend в сети `dokploy-network`
- [ ] Traefik labels добавлены в `docker-compose.production.yml`
- [ ] `curl -I http://DOMAIN/` возвращает `308 Permanent Redirect`
- [ ] `curl -I https://DOMAIN/` возвращает `HTTP/2 200`
- [ ] SSL сертификат Let's Encrypt активен

---

## 🚨 Критические грабли и их решения

### Грабля #1: Docker сети изолированы
**Проблема:** Backend не видит Supabase PostgreSQL.  
**Решение:** Backend должен быть в **двух** сетях: `dokploy-network` + `main-supabase-1kebyl`.

### Грабля #2: Nginx DNS кэширование
**Проблема:** После `docker compose up -d --force-recreate backend` frontend получает 502.  
**Решение:** Всегда перезапускайте frontend после пересоздания backend:
```bash
docker compose -f docker-compose.production.yml restart frontend
```

### Грабля #3: Неправильный DATABASE_URL
**Проблема:** Дубликат порта в connection string (`5432:5432` вместо `5432`).  
**Решение:** Используйте формат:
```
postgresql://postgres:PASSWORD@CONTAINER_NAME:5432/postgres
```
Проверяйте через `docker exec mes_backend env | grep DATABASE_URL`.

### Грабля #4: Alembic не находит миграции
**Проблема:** Неправильные пути в `alembic.ini` или Dockerfile.  
**Решение:** 
- `alembic.ini` в корне `/app`
- `script_location = backend/src/alembic`
- Миграции в `/app/backend/src/alembic/versions/`

### Грабля #5: Swagger UI не рендерится
**Проблема:** OpenAPI версия не указана явно.  
**Решение:** Добавить `openapi_version="3.1.0"` в FastAPI конфигурацию.  
**Workaround:** Использовать ReDoc вместо Swagger UI.

---

## 📝 Быстрый деплой (после первичной настройки)

```bash
# 1. Получить изменения из Git
cd /opt/mes-platform
git pull origin develop

# 2. Пересобрать и перезапустить всё
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d

# 3. Применить миграции (если есть новые)
docker exec mes_backend alembic upgrade head

# 4. Проверить статус
curl https://mes-midex-ru.factoryall.ru/api/v1/health
curl https://mes-midex-ru.factoryall.ru/

# 5. Проверить логи
docker logs mes_backend --tail 20
docker logs mes_frontend --tail 20
```

---

## 📚 Полезные ссылки

- [DOCKER_PRODUCTION.md](./DOCKER_PRODUCTION.md) — Архитектура Docker в production
- [DEPLOYMENT.md](./DEPLOYMENT.md) — Полное руководство по деплою
- [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) — Схема БД и миграции
- [API_SPEC.md](./API_SPEC.md) — Спецификация API endpoints

---

## 📧 Контакты

При возникновении проблем:
1. Проверьте Troubleshooting секцию выше
2. Проверьте логи контейнеров
3. Создайте issue в GitHub с логами и описанием проблемы

**Важно:** При создании issue приложите:
- Вывод `docker ps`
- Логи проблемного контейнера
- Конфигурацию `docker-compose.production.yml`
- Переменные окружения (без паролей!)
```

***
