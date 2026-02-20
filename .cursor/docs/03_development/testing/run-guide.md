# Запуск тестового окружения: от нуля до Расписания

Два варианта: **localhost (проще)** — одна БД, backend и скрипты на хосте; **Docker** — всё в контейнерах.

---

## Вариант 1: Localhost (проще)

Одна БД (PostgreSQL в Docker), backend и frontend на хосте. Скрипты загрузки пишут в ту же БД, что и API — нет расхождений.

### Требования

- Docker (только для postgres).
- Python 3.11+, Node.js (для frontend).
- Корень репозитория: `D:\AI\_PROJECTS\MES_midex` (или ваш путь).

### Шаг 1. Запустить только PostgreSQL

```powershell
cd D:\AI\_PROJECTS\MES_midex
docker-compose up -d postgres
```

Дождаться, пока контейнер `mes_postgres` станет healthy (порт 5432 доступен).

### Шаг 2. Окружение backend (один раз)

```powershell
cd D:\AI\_PROJECTS\MES_midex
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e backend
```

(Если venv уже есть — только активируйте: `.\venv\Scripts\Activate.ps1`.) Для конвертации xlsx→CSV при подготовке окружения нужен `openpyxl` (входит в зависимости backend). Если при шаге 4 появляется «No module named 'openpyxl'», выполните: `pip install openpyxl`.

Backend по умолчанию подключается к `postgresql://mes_user:mes_password@localhost:5432/mes_db` — это та же БД, что в контейнере (порт 5432 проброшен).

### Шаг 3. Миграции (один раз)

Запускать Alembic из каталога **backend** (путь к скриптам в alembic.ini относительный):

```powershell
cd D:\AI\_PROJECTS\MES_midex\backend
alembic -c alembic.ini upgrade head
```

(После этого можно вернуться в корень: `cd ..`.)

### Шаг 4. Подготовка тестовых данных

```powershell
cd D:\AI\_PROJECTS\MES_midex
python -m backend.src.db.prepare_test_env
```

Скрипт по порядку: датасет → только РЦ (без маршрутов) → конвертация xlsx→CSV (если есть .xlsx) → загрузка маршрутов и правил из CSV. **Тестовые данные по маршрутам и правилам берутся только из файлов** `dataset_routes.xlsx`/`.csv` и `product_routing_rules.xlsx`/`.csv`; других источников нет.

### Шаг 5. Запуск backend

```powershell
cd D:\AI\_PROJECTS\MES_midex
uvicorn backend.src.main:app --host 0.0.0.0 --port 8000 --reload --app-dir .
```

Оставить терминал открытым. API: http://localhost:8000.

В выводе backend при старте должна появиться строка **CORS allowed origins:** с `http://localhost:3000` и `http://localhost:5173`. Если при нажатии «Выпустить» на Расписании возникает **Network Error** (CORS): остановите backend (Ctrl+C), снова запустите шаг 5, обновите страницу в браузере с принудительным обновлением (Ctrl+Shift+R) и повторите «Выпустить».

### Шаг 6. Запуск frontend (второй терминал)

```powershell
cd D:\AI\_PROJECTS\MES_midex\frontend
npm install
npm run dev
```

Оставить терминал открытым. Обычно фронт: http://localhost:5173.

### Шаг 7. Проверка в браузере

1. Открыть http://localhost:5173 (или порт из вывода `npm run dev`).
2. Перейти в **Расписание**.
3. Нажать **«Проверить снова»** — должен быть зелёный статус «Система готова к запуску» (если не использовали `--backfill`, часть ГП может быть красной — это ожидаемо).
4. В блоке «Выпуск заказов в производство» нажать **«Выпустить»** у нужного заказа — задачи появятся в Ганте.

### Повторный запуск (после перезагрузки ПК / остановки)

1. `docker-compose up -d postgres`
2. Активировать venv, из корня: `uvicorn backend.src.main:app --host 0.0.0.0 --port 8000 --reload --app-dir .`
3. В другом терминале: `cd frontend && npm run dev`
4. Обновить страницу Расписания в браузере.

Данные в БД сохраняются (volume postgres). Заново грузить датасет только если нужно: снова выполнить шаг 4 (prepare_test_env).

### Сброс данных (только для тестовой версии)

На странице **Расписание** в правом верхнем углу есть кнопка **«Сбросить все данные (только для теста)»**. Она видна только в режиме разработки (`npm run dev`); в production-сборке кнопки нет. Backend тоже разрешает сброс только при `ENVIRONMENT=test` или `development`.

**После нажатия «Сбросить все данные»:**

1. Все таблицы БД очищаются (заказы, продукты, маршруты, правила, задачи и т.д.).
2. Заново подготовить данные (из корня репозитория, с активированным venv):
   ```powershell
   cd D:\AI\_PROJECTS\MES_midex
   .\venv\Scripts\Activate.ps1
   python -m backend.src.db.prepare_test_env
   ```
   Для конвертации xlsx→CSV нужен `openpyxl`; если его нет: `pip install openpyxl`.
3. Перезапустить backend (если был запущен) и обновить страницу Расписания (F5). Нажать «Проверить снова».

---

## Вариант 2: Всё в Docker

PostgreSQL, backend и frontend в контейнерах. Скрипты загрузки нужно выполнять **в той же среде**, что и backend (та же БД).

### Шаг 1. Запуск всех сервисов

```powershell
cd D:\AI\_PROJECTS\MES_midex
docker-compose up -d --build
```

Проверить: http://localhost:8000/docs (API), http://localhost:3000 (frontend).

Если при нажатии «Выпустить» на Расписании появляется **Network Error** и в консоли браузера — **CORS**: перезапустите backend, чтобы подхватить переменные `CORS_ORIGINS` и `ENVIRONMENT` из `docker-compose.yml`:  
`docker-compose restart backend`

### Шаг 2. Миграции (один раз)

```powershell
docker-compose exec backend alembic -c /app/backend/alembic.ini upgrade head
```

### Шаг 3. Тестовые данные: скрипт с хоста в БД Docker

Backend в Docker подключается к `postgres:5432`. С хоста к этой БД можно подключиться как к `localhost:5432` (порт проброшен). Запуск **с хоста** с явным указанием БД:

```powershell
cd D:\AI\_PROJECTS\MES_midex
.\venv\Scripts\Activate.ps1
$env:DATABASE_URL = "postgresql://mes_user:mes_password@localhost:5432/mes_db"
python -m backend.src.db.prepare_test_env
```

Так скрипт пишет в ту же БД, что и backend в Docker. После этого **перезапустить backend**, чтобы подхватить данные:

```powershell
docker-compose restart backend
```

### Шаг 4. Проверка в браузере

1. Открыть http://localhost:3000.
2. Перейти в **Расписание** → **«Проверить снова»**.
3. Выпуск заказов и Гант — как в варианте 1.

**Сброс данных (только для теста):** на странице Расписание в dev-режиме доступна кнопка «Сбросить все данные». После сброса — заново выполнить подготовку данных (см. шаг 3 или альтернативу ниже) и перезапустить backend.

### Альтернатива: выполнить скрипт внутри контейнера

Если нужен запуск внутри backend-контейнера (например, нет venv на хосте), нужно пробросить каталог с CSV:

1. В `docker-compose.yml` у backend в `volumes` добавить (временно):
   `- ./.cursor:/app/.cursor:ro`
2. Перезапустить: `docker-compose up -d backend`
3. Выполнить:
   ```powershell
   docker-compose exec backend python -m backend.src.db.prepare_test_env
   ```

После этого снова нажать «Проверить снова» на странице Расписания.

---

## Сводка

| Действие              | Localhost (проще)                          | Docker (всё в контейнерах)                    |
|-----------------------|--------------------------------------------|-----------------------------------------------|
| БД                    | `docker-compose up -d postgres`            | `docker-compose up -d`                        |
| Миграции              | `alembic ... upgrade head` с хоста         | `docker-compose exec backend alembic ...`     |
| Подготовка данных     | `python -m backend.src.db.prepare_test_env` с хоста | С хоста с `DATABASE_URL=...localhost:5432...` или exec в backend с примонтированным `.cursor` |
| Backend               | `uvicorn ...` с хоста                      | Контейнер `mes_backend`                       |
| Frontend              | `npm run dev` в frontend/                  | Контейнер на порту 3000                       |
| Одна БД для всего     | Да (localhost:5432)                        | Да, если скрипт с хоста с `DATABASE_URL=localhost:5432` или exec в backend |

Рекомендация для проверки: **вариант 1 (localhost)** — меньше шагов и нет путаницы с БД.
