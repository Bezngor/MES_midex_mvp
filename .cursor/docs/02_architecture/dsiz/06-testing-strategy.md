## 6. Testing & Validation Strategy (Тестирование DSIZ)

### 6.1. Принципы

**Core-тесты** неизменны (93%). **DSIZ-тесты** — `backend/tests/customizations/dsiz/`. 

**Покрытие:** **90%+** для unit/integration. 

**Запуск:**
```bash
pytest tests/customizations/dsiz/ -v --cov=backend/customizations/dsiz --cov-report=html --cov-fail-under=90
```

***

### 6.2. Unit-тесты сервисов

#### 6.2.1. DSIZMRPService
- Under-loading реактора.
- CIP-блокировка понедельник shift 1.
- Остатки Bulk.

#### 6.2.2. DSIZDispatchingService
- Лимит 2 варки/смену.
- Changeover matrix.
- Workforce constraints.
- Ручные блокировки.
- QR-зависимости.

#### 6.2.3. DSIZWorkforceService
- Деградация авто-линии (3/4 оператора = 0.5 rate).
- Блокировка тубировки без упаковщика.

***

### 6.3. Integration-тесты API

`test_dsiz_api_routes.py` — полный стек `/dsiz/planning/run` с edge-кейсами (CIP, workforce, QR, блокировки).

***

### 6.4. E2E-тесты (Playwright)

`frontend/e2e/dsiz.spec.ts`:
- Полный флоу: planning → actualize → пересчёт.

***

### 6.5. Тестовые данные

#### **Рекомендация: 12 SKU** (для полного покрытия):

**Распределение:**
```
Реактор (Паста): 3 SKU (разные объёмы/совместимость)
Реактор (Крем): 3 SKU
Кубы (Гели/Мыло/Спреи): 3 SKU
Тубировка: 2 SKU (паста + крем)
Авто-розлив: 1 SKU (мыло)
```

**Обоснование:** покрывает все комбинации оборудования, режимов, changeover-групп.

**Fixtures:**
- `test_dsiz_data.sql` — 12 продуктов + справочники.
- `test_plans.json` — 10+ сценариев (номинал, CIP, workforce, QR-delay, блокировки).

***

### 6.6. CI/CD (GitHub Actions)

`.github/workflows/dsiz-tests.yml` — pytest + cov 90%+.

**Деплой-блокер:**
```bash
pytest tests/customizations/dsiz/ --cov-fail-under=90
```

***

### 6.7. Checklist перед коммитом

```
✅ pytest dsiz/ -v (зелёные тесты)
✅ Coverage 90%+ dsiz/
✅ Core-тесты не сломаны
✅ E2E проходят
✅ Swagger обновлён
✅ README с примерами
```

***