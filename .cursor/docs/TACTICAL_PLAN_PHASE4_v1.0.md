---
name: Phase 4 Tactical Plan
version: 1.0
status: approved
role: tactical_plan
overview: >
  Утверждённый тактический план Phase 4 (Advanced Features) для MES Platform v1.2.0-dsiz.
  Используется как рабочий план итераций и файл переноса контекста между сессиями.
maintenance_rules:
  - После каждой успешной итерации/корректировки/теста статусы задач и подпунктов в этом плане
    должны быть актуализированы (pending/in_progress/completed/blocked).
  - Все правки UI/UX, предлагаемые пользователем, должны быть проанализированы на соответствие
    основной бизнес-логике; при конфликте требуется явное подтверждение пользователя.
  - Этот файл используется как основной источник правды по состоянию Phase 4 и
    как документ переноса контекста между чатами при исчерпании контекстного окна.
  - Любые изменения плана должны быть отражены как в текстовой части документа, так и в
    секции todos.
todos:
  - id: seed-data-load
    content: Загрузить seed данные (seed_dsiz_data.sql) в тестовую БД и проверить корректность загрузки
    status: completed
  - id: module-testing-backend
    content: Провести полное тестирование backend модулей (MRP, Dispatching, Workforce) на seed данных через автотесты
    status: completed
  - id: module-testing-frontend
    content: Провести ручное тестирование всех frontend страниц и компонентов DSIZ на seed данных
    status: pending
  - id: integration-testing
    content: Провести интеграционное тестирование полных flow (планирование → диспетчеризация → выполнение) на seed данных
    status: pending
  - id: ui-feedback-collection
    content: Собрать feedback по использованию интерфейса и внести правки (с запросом подтверждения при конфликте с логикой)
    status: pending
  - id: auto-create-batches-from-planning
    content: Автоматическое создание партий (Batch, PLANNED) по результатам планирования DSIZ (выбор РЦ, смены → создание записей в БД)
    status: pending
  - id: gantt-drag-drop
    content: Реализовать drag & drop для операций в DsizGanttChart с валидацией конфликтов
    status: pending
  - id: gantt-backend-api
    content: Создать PATCH endpoint для обновления времени операций с автоматическим пересчётом зависимостей
    status: pending
  - id: websocket-backend
    content: Реализовать WebSocket сервер для real-time обновлений планирования
    status: pending
  - id: websocket-frontend
    content: Создать useWebSocket hook и интегрировать с Gantt chart для автоматических обновлений
    status: pending
  - id: advanced-dispatching
    content: Расширить DSIZDispatchingService приоритетной диспетчеризацией и разрешением конфликтов
    status: pending
  - id: reschedule-api
    content: Добавить API endpoint для динамического перепланирования при изменениях
    status: pending
  - id: oee-backend
    content: Реализовать расчёт OEE метрик и хранение в БД
    status: pending
  - id: oee-dashboard
    content: Создать OEE дашборд с графиками и фильтрами
    status: pending
  - id: mobile-responsive
    content: Адаптировать все DSIZ страницы для мобильных устройств
    status: pending
  - id: frontend-tests
    content: Настроить Jest/RTL и добавить тесты для DSIZ компонентов
    status: pending
  - id: websocket-tests
    content: Добавить тесты для WebSocket handlers и конфликт-резолюции
    status: pending
  - id: erp-integration-design
    content: Спроектировать архитектуру ERP интеграции (1C/SAP) и создать базовый сервис
    status: pending
---

# Тактический план Phase 4: Advanced Features (v1.2.0-dsiz)

## 1. Назначение документа

- **Утверждённый тактический план:** данный файл фиксирует согласованный с владельцем проекта план работ Phase 4.
- **Операционный инструмент:** используется как чек-лист и дорожная карта для итераций разработки, тестирования и доработок.
- **Перенос контекста:** является основным файлом переноса контекста между чатами/сессиями при исчерпании контекстного окна.
- **Единый источник правды:** состояние задач Phase 4 (что сделано, что в работе, что заблокировано) отражается именно здесь.

## 2. Регламент использования и обновления плана

- **2.1 Обновление статусов задач**
  - После каждой успешной итерации, корректировки кода или прохождения тестов
    статусы соответствующих задач/подзадач в секции `todos` и в тексте плана
    должны быть обновлены:
    - `pending` → задача ещё не начата;
    - `in_progress` → активно выполняется;
    - `completed` → реализована, протестирована, задокументирована;
    - `blocked` → временно заблокирована (указать причину в тексте).

- **2.2 Работа с предложениями по UI/UX**
  - Любые предложения пользователя по изменению интерфейса или поведения
    должны быть:
    - проанализированы на соответствие доменной логике и архитектурным правилам (см. `MES_RULES.md`, `PROJECT_MANIFEST_v1.1.md`);
    - если изменение **конфликтует** с основной логикой — **обязательно** запрашивается отдельное подтверждение пользователя
      с объяснением возможных последствий;
    - только после явного подтверждения такие изменения вносятся и фиксируются в этом плане.

- **2.3 Роль файла в переносе контекста**
  - При исчерпании контекстного окна новый диалог должен поднимать текущий контекст
    из следующих файлов:
    - `CONTEXT_STACK_v1.1.md` — общий контекст проекта;
    - `PROJECT_MANIFEST_v1.1.md` — состояние проекта и фазы;
    - `TACTICAL_PLAN_PHASE4_v1.0.md` — детальный тактический план Phase 4 (этот файл).
  - В начале нового диалога необходимо кратко резюмировать:
    - текущие статусы ключевых задач из `todos`;
    - последние выполненные итерации и принятые решения.

- **2.4 Изменения самого плана**
  - Любое изменение структуры плана (добавление/удаление разделов, смена приоритетов)
    должно:
    - быть согласовано в чате;
    - быть отражено как в тексте разделов, так и в секции `todos`;
    - по возможности сопровождаться краткой пометкой/датой изменения в тексте.

---

# План разработки Phase 4: Advanced Features (v1.2.0-dsiz)

## Текущий контекст

**Завершено (Phase 3):**

- ✅ Frontend: 3 страницы (Planning, Shift Actualize, Master Data), 5 компонентов DSIZ
- ✅ Backend: 3 сервиса (MRP, Dispatching, Workforce), 2 API роутера, 5 таблиц БД
- ✅ Production: v1.1.0-dsiz deployed (29.01.2026), 93% test coverage
- ✅ Infrastructure: Traefik UP, GitFlow workflow установлен

**Цель Phase 4:** Расширение функциональности для production-ready системы с real-time возможностями и интеграциями.

---

## 0. Тестирование на seed данных и доработка UI

### Задачи:

- **0.1** Загрузка seed данных — ✅ **выполнено**:
  - Применить `backend/src/db/seed_dsiz_data.sql` в тестовую БД
  - Проверить корректность загрузки всех DSIZ таблиц (work_center_modes, changeover_matrix, product_routing, base_rates, workforce_requirements)
  - Убедиться, что связанные данные (продукты, рабочие центры) существуют или создать их
  - Валидация целостности данных (foreign keys, constraints)
  - **Результат:** Создана утилита `backend/src/db/seed_dsiz_loader.py`, seed применён (15 выражений). Сводка: Work Center Modes 2, Changeover Matrix 12, Product Routing 8, Base Rates 8, Workforce Requirements 4.

- **0.2** Автоматическое тестирование модулей — ✅ **выполнено**:
  - Запустить все существующие автотесты на seed данных: `pytest tests/ --cov=backend -v`
  - Проверить coverage для DSIZ модулей (цель: 91%+)
  - Добавить недостающие тесты для edge cases на реальных seed данных
  - Проверить работу всех API endpoints с seed данными
  - **Результат:** DSIZ тесты: 90 passed, coverage 92% (цель 91%+ достигнута). Все модули (MRP, Dispatching, Workforce) протестированы.

- **0.3** Ручное тестирование модулей:
  - **Backend модули:**
    - DSIZMRPService: запуск планирования на seed данных, проверка расчётов
    - DSIZDispatchingService: диспетчеризация задач с учётом seed конфигураций
    - DSIZWorkforceService: проверка расчёта персонала по сменам
  - **Frontend страницы:**
    - DsizPlanningPage: заполнение формы, запуск планирования, просмотр результатов
    - DsizShiftActualizePage: актуализация смен, ввод фактических данных
    - DsizMasterDataPage: просмотр и редактирование справочников
  - **Компоненты:**
    - ReactorSlotSelector: выбор слотов реакторов (1-12)
    - WorkforceInput: ввод персонала по сменам
    - LabelingModeSelector: выбор режима маркировки
    - DsizGanttChart: визуализация операций планирования

- **0.4** Интеграционное тестирование flow:
  - Полный цикл: создание ManufacturingOrder → планирование → диспетчеризация → выполнение задач
  - Проверка работы с реальными продуктами из seed (кремы GECO, пасты СЕВЕРЯНИН, жидкое мыло)
  - Тестирование конфликтов и их разрешения (переналадки, персонал, слоты)
  - Проверка валидации бизнес-правил на seed данных

- **0.5** Сбор feedback и внесение правок:
  - Собрать вопросы и предложения по использованию интерфейса
  - Проанализировать каждое предложение на соответствие бизнес-логике
  - **КРИТИЧНО:** Если предложение идёт вразрез основной логике — **обязательно запросить подтверждение** у пользователя перед внесением изменений
  - Внести одобренные правки в UI/UX
  - Документировать все изменения и их обоснование

- **0.6** Автоматическое создание партий по результатам планирования (бэклог после блока 0):
  - По результатам DSIZ планирования (нетто-потребность, выбор РЦ и смен) автоматически создавать записи Batch в БД со статусом PLANNED.
  - Связь операций плана с созданными партиями (опционально — parent_order_id, work_center_id, planned_start по смене).
  - **Контекст:** Сейчас планирование возвращает только список операций (PlanningOperation); записи в таблице `batches` не создаются. Ручное создание партий остаётся для принудительных варок.

**Файлы для работы:**

- `backend/src/db/seed_dsiz_data.sql` — seed скрипт (проверить и дополнить при необходимости)
- `backend/tests/customizations/dsiz/` — добавить тесты на seed данных
- `frontend/src/pages/DsizPlanningPage.tsx` — правки по feedback
- `frontend/src/components/dsiz/*` — правки компонентов по feedback
- `backend/customizations/dsiz/services/*` — правки бизнес-логики (только после подтверждения)

---

## 1. Интерактивный Gantt Chart (Drag & Drop)

### Задачи:

- **1.1** Расширить `DsizGanttChart.tsx`:
  - Добавить drag & drop для операций (изменение времени начала/окончания)
  - Визуальная индикация конфликтов при перетаскивании
  - Контекстное меню (редактировать, удалить, заблокировать)

- **1.2** Backend API для обновления операций:
  - `PATCH /api/v1/dsiz/planning/operations/{operation_id}` — изменение времени операции
  - Валидация конфликтов (пересечение слотов, персонал, переналадки)
  - Автоматический пересчёт зависимых операций

- **1.3** State management:
  - Интеграция с React Query для optimistic updates
  - Обработка конфликтов (rollback при ошибке валидации)
  - Undo/Redo функциональность (опционально)

**Файлы для изменения:**

- `frontend/src/components/dsiz/DsizGanttChart.tsx` — добавить drag handlers
- `frontend/src/hooks/useDsizPlanning.ts` — методы updateOperation, validateOperation
- `backend/customizations/dsiz/routes/dsiz_planning_routes.py` — PATCH endpoint
- `backend/customizations/dsiz/services/dsiz_mrp_service.py` — метод `update_operation_time()`

---

## 2. Real-time Updates (WebSocket)

### Задачи:

- **2.1** Backend WebSocket сервер:
  - FastAPI WebSocket endpoint `/ws/dsiz/planning/{plan_id}`
  - Broadcast изменений операций всем подключённым клиентам
  - Обработка подключений/отключений

- **2.2** Frontend WebSocket клиент:
  - Hook `useWebSocket.ts` для подключения к WebSocket
  - Автоматическое обновление Gantt chart при изменениях от других пользователей
  - Индикатор "онлайн" пользователей, работающих с планом

- **2.3** Конфликт-резолюция:
  - Оптимистичные блокировки (кто редактирует операцию)
  - Уведомления о конфликтах редактирования
  - Merge стратегия для одновременных изменений

**Файлы для создания:**

- `backend/customizations/dsiz/routes/websocket_routes.py` — WebSocket handlers
- `backend/customizations/dsiz/services/websocket_manager.py` — управление подключениями
- `frontend/src/hooks/useWebSocket.ts` — WebSocket hook
- `frontend/src/services/websocket.ts` — WebSocket клиент

---

## 3. Advanced Dispatching

### Задачи:

- **3.1** Приоритетная диспетчеризация:
  - Расширить `DSIZDispatchingService` методом `dispatch_with_priority()`
  - Учёт приоритетов ManufacturingOrder (HIGH, MEDIUM, LOW)
  - Динамическая переоценка приоритетов на основе due date

- **3.2** Разрешение конфликтов оборудования:
  - Автоматическое обнаружение конфликтов слотов реакторов
  - Предложения по переносу операций (rescheduling suggestions)
  - Визуализация конфликтов в UI

- **3.3** Динамическое перепланирование:
  - API endpoint `POST /api/v1/dsiz/dispatching/reschedule`
  - Пересчёт при изменении состояния (задержка, отмена, новый заказ)
  - Минимизация disruption существующего плана

**Файлы для изменения:**

- `backend/customizations/dsiz/services/dsiz_dispatching_service.py` — методы приоритизации
- `backend/customizations/dsiz/routes/dsiz_dispatching_routes.py` — reschedule endpoint
- `frontend/src/pages/DsizPlanningPage.tsx` — UI для конфликтов и reschedule

---

## 4. ERP Integration (1C/SAP Sync)

### Задачи:

- **4.1** Архитектура интеграции:
  - Спроектировать схему синхронизации (ManufacturingOrder, Product, Inventory)
  - Выбрать протокол (REST API, SOAP, файловый обмен)
  - Определить mapping полей (1C/SAP → MES)

- **4.2** Backend интеграционный сервис:
  - `ERPIntegrationService` в `backend/customizations/dsiz/services/`
  - Методы: `sync_orders()`, `sync_products()`, `sync_inventory()`
  - Обработка ошибок и retry логика

- **4.3** Планировщик синхронизации:
  - Периодическая синхронизация (n8n workflow или Celery)
  - Логирование синхронизаций в таблицу `erp_sync_logs`
  - UI для ручного запуска и просмотра логов

**Файлы для создания:**

- `backend/customizations/dsiz/services/erp_integration_service.py` — интеграционный сервис
- `backend/customizations/dsiz/models/erp_sync_logs.py` — модель логов
- `backend/customizations/dsiz/routes/erp_routes.py` — API для управления синхронизацией
- `frontend/src/pages/ErpSyncPage.tsx` — страница управления синхронизацией

---

## 5. Performance Monitoring (OEE Tracking)

### Задачи:

- **5.1** Backend метрики OEE:
  - Расчёт OEE (Overall Equipment Effectiveness) = Availability × Performance × Quality
  - Метрики по WorkCenter: uptime, downtime, throughput, reject rate
  - Хранение исторических данных в `oee_metrics` таблице

- **5.2** Real-time KPI дашборды:
  - Компонент `OEEDashboard.tsx` с графиками (Recharts)
  - Метрики: OEE %, Availability %, Performance %, Quality %
  - Фильтры по дате, WorkCenter, смене

- **5.3** Алерты и уведомления:
  - Пороговые значения для OEE (например, < 70% = warning)
  - Email/WebSocket уведомления при падении метрик
  - История алертов в UI

**Файлы для создания:**

- `backend/customizations/dsiz/models/oee_metrics.py` — модель метрик
- `backend/customizations/dsiz/services/oee_service.py` — расчёт OEE
- `backend/customizations/dsiz/routes/oee_routes.py` — API метрик
- `frontend/src/pages/OEEDashboardPage.tsx` — дашборд OEE
- `frontend/src/components/dsiz/OEEMetricsChart.tsx` — графики метрик

---

## 6. Mobile-Responsive UI

### Задачи:

- **6.1** Адаптация существующих страниц:
  - Оптимизация `DsizPlanningPage` для мобильных (responsive grid)
  - Упрощённая навигация для touch-устройств
  - Touch-friendly компоненты (крупные кнопки, swipe gestures)

- **6.2** Мобильные компоненты:
  - `MobileGanttChart.tsx` — упрощённая версия для маленьких экранов
  - `MobileTaskCard.tsx` — карточки задач для мобильных
  - Bottom navigation bar вместо sidebar

**Файлы для изменения:**

- Все страницы в `frontend/src/pages/` — добавить responsive classes
- `frontend/src/components/dsiz/DsizGanttChart.tsx` — мобильная версия
- `frontend/src/App.tsx` — адаптивная навигация

---

## 7. Testing & Quality Assurance

### Задачи:

- **7.1** Frontend тесты:
  - Настроить Jest + React Testing Library
  - Unit тесты для компонентов DSIZ (минимум 80% coverage)
  - Integration тесты для useDsizPlanning hook

- **7.2** Backend тесты:
  - Тесты для WebSocket handlers
  - Тесты для ERP интеграции (mock ERP API)
  - Тесты для OEE расчётов

- **7.3** E2E тесты (опционально):
  - Playwright/Cypress для критичных flow (планирование, диспетчеризация)

---

## Приоритизация задач

**Must Have (для v1.2.0-dsiz):**

0. Тестирование на seed данных и доработка UI — базовая стабильность перед новыми фичами  
1. Интерактивный Gantt Chart (drag & drop) — критично для UX  
2. Real-time Updates (WebSocket) — конкурентное преимущество  
3. Advanced Dispatching — базовая функциональность  

**Should Have:**

4. Performance Monitoring (OEE) — важно для production  
5. Mobile-Responsive UI — улучшает доступность  

**Nice to Have (можно отложить на Phase 5):**

6. ERP Integration — зависит от доступности ERP API  
7. Расширенное тестирование — можно делать параллельно  

---

## Бэклог (после ручного тестирования)

- **Визуализация Gantt при 14 и 30 днях:** отдельно проверить отображение расписания при выборе «14 дней» и «30 дней» (корректность сетки и секторов по рабочим центрам).

---

## Критерии готовности Phase 4

- [ ] Seed данные загружены и проверены
- [ ] Все модули протестированы на seed данных (автотесты + ручное тестирование)
- [ ] Интеграционные flow работают корректно на seed данных
- [ ] Feedback по UI собран и внесены одобренные правки
- [ ] Drag & drop работает для операций в Gantt chart
- [ ] WebSocket обновления работают (2+ клиента видят изменения)
- [ ] Advanced dispatching с приоритетами работает
- [ ] OEE дашборд показывает метрики
- [ ] Мобильная версия работает на основных страницах
- [ ] Test coverage не ниже 91% (DSIZ), 93% (global)
- [ ] Все тесты зелёные перед release
- [ ] Документация обновлена (API docs, deployment guide)

