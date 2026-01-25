## Модуль 7: Deployment & Rollout Plan (Деплой и запуск)

### 7.1. GitOps Workflow

**Цикл разработки → прод:**
```bash
# 1. Локальная разработка (Cursor)
git checkout develop
git pull origin develop
# код + тесты

# 2. Проверка
pytest tests/customizations/dsiz/ --cov-fail-under=90
pytest tests/  # core не сломан

# 3. Коммит
git add .
git commit -m "feat(dsiz): add product_work_center_routing support"

# 4. Деплой
git push origin develop
ssh root@185.177.94.29 "cd /root/mes-platform && git pull origin develop && docker compose -f docker-compose.production.yml up -d --build"
curl https://mes-midex-ru.factoryall.ru/api/v1/dsiz/health
```

### 7.2. Миграции БД

**После каждого фичевого коммита:**
```bash
ssh root@185.177.94.29
cd /root/mes-platform
alembic upgrade head
psql supabase_db -f migrations/dsiz_latest.sql  # начальные данные
```

### 7.3. Rollout Phases

#### **Phase 1: MVP Core (2 недели)**
```
✅ DSIZMRPService (under-loading, CIP)
✅ DSIZWorkforceService (базовые нормы)
✅ /dsiz/planning/run (базовый)
✅ Тесты 90%+
✅ Деплой на production
```

#### **Phase 2: Dispatching + Routing (2 недели)**
```
✅ dsiz_product_work_center_routing
✅ DSIZDispatchingService (routing + changeover)
✅ /dsiz/shift-actualize
✅ Drag&drop Gantt
```

#### **Phase 3: Admin + Справочники (1 неделя)**
```
✅ /dsiz/master-data (все вкладки)
✅ Пакетная загрузка CSV
✅ Frontend E2E
```

#### **Phase 4: Production Validation (1 неделя)**
```
✅ Мониторинг логов
✅ Производственный тест (1 смена)
✅ Power BI views
✅ Доработки по фидбеку
```

### 7.4. Health Checks & Monitoring

**API Health:**
```
GET /api/v1/dsiz/health → {"status": "ok", "dsiz_version": "v1.0", "coverage": "92%"}
```

**Docker logs:**
```bash
docker logs mes-backend --tail 50 | grep "DSIZ"
```

**Метрики:**
- `dsiz_planning_duration_ms`
- `dsiz_operations_planned_count`
- `dsiz_workforce_violations_count`

### 7.5. Rollback Plan

**При проблемах:**
```bash
ssh root@185.177.94.29
cd /root/mes-platform
git checkout main  # или template-base
git pull origin main
docker compose down
docker compose -f docker-compose.production.yml up -d --build
```

### 7.6. Post-Deployment Checklist

```
✅ curl /api/v1/dsiz/planning/run → 200 OK
✅ curl /api/v1/health → core OK
✅ docker logs → нет ERROR
✅ pytest tests/customizations/dsiz/ → remotely OK
✅ Frontend: /dsiz/planning загружается
✅ БД: новые таблицы созданы
```

***