## 5. Frontend Customization (Фронтенд)

### 5.1. Общий подход

**Core фронтенд** остаётся универсальным. DSIZ-кастомизация: 

- Новые страницы: `/dsiz/planning`, `/dsiz/shift-actualize`, `/dsiz/master-data`.
- Расширения существующих через слоты.
- Компоненты: `frontend/src/components/dsiz/`.

***

### 5.2. Новые страницы

#### 5.2.1. `/dsiz/planning` (DsizPlanningPage, роль: planner, admin)

- Форма запуска DSIZ-планирования (дата, горизонт, блокировки, workforce, QR).
- Gantt-план:
  - цветовая индикация типов операций,
  - слоты реактора (1/2),
  - setup-время из changeover.
- Кнопки: пересчёт, экспорт CSV, утверждение.
- **Drag&drop:** планируется на Phase 2 (сдвиг операций между слотами/сменами).

#### 5.2.2. `/dsiz/shift-actualize` (DsizShiftActualizePage, роль: dispatcher, admin)

**Уточнение роли shift_master (заглушка на MVP):**
- Пока роль не утверждена в штате, функционал доступен `dispatcher`/`admin`.
- **shift_master видит ТОЛЬКО свою смену** (по JWT: текущий пользователь привязан к смене).
- Задания смены утверждает Начальник производства (`planner`/`admin`), затем передаёт исполнителям:
  - **операторам оборудования** (автоматически),
  - **безоператорным участкам** — конкретным работникам смены (указывает Начальник).

**Функционал:**
- Выбор смены → форма фактизации:
  - **Люди:** таблица ролей по станкам (доступные/недостающие).
  - **Блокировки:** ручные блоки оборудования.
  - **QR:** статус по задачам смены.
- Автопересчёт плана смены.
- Кнопки: «Сохранить факт», «Напечатать задание смены» (PDF).
- **Мобильная адаптация:** приоритетная (планшет/телефон для исполнителей).

#### 5.2.3. `/dsiz/master-data` (DsizMasterDataPage, роль: admin)

**Единая страница с вкладками:**
1. Режимы реактора (`dsiz_work_center_modes`).
2. Матрица совместимости.
3. Базовые скорости.
4. Workforce правила.
5. Правила маркировки.

**CRUD + пакетная загрузка/экспорт CSV/Excel.**

***

### 5.3. Расширения core-страниц

#### `/planning`:
- Панель «DSIZ Ограничения» (реактор, CIP, workforce).
- Фильтр «Только DSIZ операции».

#### `/resources`:
- Колонки DSIZ-полей.
- Вкладки Workforce/Labeling по станку.

#### `/orders`:
- `dsiz_labeling_mode`, статус QR (жёлтая метка при задержке).

***

### 5.4. Компоненты DSIZ

- `ReactorSlotSelector` — выбор слота 1/2.
- `ChangeoverMatrixEditor` — цветовая таблица матрицы.
- `WorkforceInput` — ввод состава смены + резерв.
- `LabelingModeSelector` — AUTO/MANUAL + статус принтера.

***

### 5.5. Custom Hooks

- `useDsizPlanning(planningDate, horizonDays)` — запуск/план.
- `useShiftActualize(shiftDate, shiftNum)` — фактизация смены.

***

### 5.6. Роутинг

```typescript
<Route path="/dsiz/planning" element={<DsizPlanningPage />} />
<Route path="/dsiz/shift-actualize" element={<DsizShiftActualizePage />} />
<Route path="/dsiz/master-data" element={<DsizMasterDataPage />} />
```

**Sidebar:**
```
📊 Планирование
├── Универсальное
└── DSIZ
👥 Смены
├── Универсальное  
└── Фактизация DSIZ (shift_master)
⚙️ Справочники DSIZ (admin)
```

***

### 5.7. Интеграция и особенности

**Core-подхват:**
- Gantt автоматически показывает DSIZ-поля (`reactor_slot`, `setup_time`).
- Фильтры по DSIZ Work Centers.

**Мобильность:**
- `/dsiz/shift-actualize` — responsive-first (планшеты исполнителей).
- PDF-задания смены для печати/распространения.

**i18n:** `dsiz.reactor.slot1`, `dsiz.shift.actualize`, `dsiz.qr.delayed`.

**Drag&drop Gantt:** Phase 2 (сдвиг операций между слотами/сменами).

***