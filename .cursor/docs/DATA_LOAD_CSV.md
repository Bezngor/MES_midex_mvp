# Загрузка датасета из CSV (заказы + BOM)

**Назначение:** Заполнить БД тестовыми данными из файлов заказов покупателей и BOM для проверки MRP и сквозных сценариев.

## Быстрый старт (тестовое окружение)

Полная последовательность «от нуля до Расписания» (localhost или Docker): см. **TEST_RUN_GUIDE.md** в корне репозитория.

Кратко: из **корня репозитория** с активированным venv выполнить `python -m backend.src.db.prepare_test_env`, затем перезапустить backend и обновить страницу «Расписание».

---

## Файлы

- **Заказы:** `.cursor/_olds/info/dataset_customer_orders.csv`  
  Колонки: `Наименование;Код продукции;Статус заказа;Дата отгрузки;Номер заказа;Покупатель;Количество`  
  Статус: «Отгрузить» → приоритет HIGH, «В работе» → NORMAL. Все заказы создаются со статусом **SHIP**.

- **BOM:** `.cursor/_olds/info/dataset_bom.csv`  
  Колонки: `Номенклатура;_Наименование;Доля;Категория`  
  Категория «Продукция» = ГП → Масса/Упаковка; «Масса» = Масса → Сырьё.  
  **Источник:** при наличии `dataset_bom.xlsx` в той же папке CSV можно получить конвертацией:  
  `python -m backend.src.db.xlsx_to_csv` (создаёт/обновляет `dataset_bom.csv`).  
  Скрипт `prepare_test_env` перед загрузкой датасета автоматически конвертирует BOM из xlsx, если файл есть.

## Правила загрузки

- В датасет попадают только ГП, которые есть **и в заказах, и в BOM** (сопоставление по наименованию).
- Загружаются только продукты и строки BOM, реально задействованные в этих заказах (ГП → Масса/Упаковка → Сырьё по цепочке).
- Перед загрузкой очищаются таблицы: products, bill_of_materials, manufacturing_orders и зависимые (production_tasks, batches, inventory_balances, **manufacturing_routes**, **product_routing_rules**, work_centers и т.д.). После загрузки датасета **обязательно** выполните шаги 2 и 3 ниже (посев РЦ и загрузка маршрутов/правил из CSV).

## Запуск

Из **корня репозитория**, с активированным окружением (venv / backend deps):

```bash
# Только статистика, без изменений БД
python -m backend.src.db.load_dataset_from_csv --dry-run

# Загрузка (файлы по умолчанию)
python -m backend.src.db.load_dataset_from_csv

# Свои файлы
python -m backend.src.db.load_dataset_from_csv --orders path/to/orders.csv --bom path/to/bom.csv
```

Скрипт: `backend/src/db/load_dataset_from_csv.py`.

---

## После загрузки: оборудование и маршруты

Чтобы заказы можно было **выпускать в производство** и видеть задачи в Ганте:

1. **Миграции** (если ещё не применены):
   ```bash
   alembic -c backend/alembic.ini upgrade head
   ```

2. **Посев только РЦ** (маршруты не создаются — они загружаются только из CSV):
   При использовании `prepare_test_env` шаг 2 выполняет только `seed_work_centers`. Маршруты и правила выбора РЦ берутся **только** из `dataset_routes.xlsx`/`.csv` и `product_routing_rules.xlsx`/`.csv` (при наличии .xlsx выполняется конвертация в CSV, затем загрузка).

3. **Загрузка маршрутов и правил выбора РЦ из CSV** (обязательно после загрузки датасета, иначе выпуск заказов будет заблокирован):
   ```bash
   python -m backend.src.db.load_routes_from_csv
   python -m backend.src.db.load_routes_from_csv --routes path/to/dataset_routes.csv --rules path/to/product_routing_rules.csv
   ```
   Файлы по умолчанию: `.cursor/_olds/info/dataset_routes.csv`, `.cursor/_olds/info/product_routing_rules.csv`. Обновляет manufacturing_routes и route_operations по коду ГП, загружает правила выбора РЦ в таблицу `product_routing_rules`. В Docker: при необходимости смонтируйте корень проекта или передайте пути к CSV внутри контейнера через `--routes` и `--rules`.

   **Проверка готовности:** на странице «Расписание» вызывается GET `/api/v1/validation/routes-and-rules`. Если у каких-то ГП нет записей в маршрутах или в правилах выбора РЦ — показывается список этих ГП; выпуск заказов блокируется. После загрузки маршрутов **перезапустите backend** (uvicorn или контейнер), затем нажмите «Проверить снова».

4. **Этап 1 — загрузка оборудования работой и Гант:**
   - Открыть вкладку **Расписание**.
   - В блоке «Выпуск заказов в производство» нажать **Выпустить** у нужных заказов (SHIP/PLANNED).
   - Задачи появятся в Ганте (по рабочим центрам).

5. **Этап 2 — оформление смены:** вкладка **DSIZ Shift Actualize** (после этапа 1).

---

## Загрузка остатков (Inventory)

Для тестирования MRP (нетто-потребность, доступный запас) нужны остатки по ГП, Массе и Сырью.

### Шаг 1: Экспорт списка продуктов

Из **корня репозитория** (с активированным venv):

```bash
python -m backend.src.db.export_products_for_inventory
python -m backend.src.db.export_products_for_inventory -o path/to/products_for_inventory.csv
```

Создаётся CSV с колонками: `product_id`, `product_code`, `product_name`, `product_type`, `unit_of_measure`, `location`, `quantity`, `product_status`, `reserved_quantity`. Последние четыре колонки пустые — их заполняет пользователь.

Файл по умолчанию: `.cursor/_olds/info/products_for_inventory.csv`.

### Шаг 2: Заполнение остатков в Excel

1. Откройте `products_for_inventory.csv` в Excel (разделитель — точка с запятой, кодировка UTF-8).
2. Заполните для нужных строк:
   - **location** — локация (например `CUB_1`, `MAIN`, `WH_1`).
   - **quantity** — количество (число).
   - **product_status** — `FINISHED` или `SEMI_FINISHED` (для массы обычно `SEMI_FINISHED`, для ГП и сырья — `FINISHED`). В интерфейсе «Остатки» статус FINISHED отображается как **«Готово к отпуску»** (сырьё, масса и ГП — единая формулировка).
   - **reserved_quantity** — зарезервировано (по умолчанию 0).
3. Сохраните как **inventory.xlsx** (или другой путь) в `.cursor/_olds/info/` или передайте путь при конвертации.

Строки без `location` или `quantity` при загрузке пропускаются. Один продукт может иметь несколько строк (разные локации и/или статусы).

### Шаг 3: Конвертация xlsx → CSV

```bash
python -m backend.src.db.xlsx_to_csv --inventory path/to/inventory.xlsx --out-inventory path/to/inventory.csv
```

Файлы по умолчанию: `--inventory .cursor/_olds/info/inventory.xlsx`, `--out-inventory .cursor/_olds/info/inventory.csv`. Поддерживаются русские заголовки: Код, Локация, Количество, Статус, Зарезервировано.

### Шаг 4: Загрузка остатков в БД

```bash
python -m backend.src.db.load_inventory_from_csv -f path/to/inventory.csv
```

По умолчанию читается `.cursor/_olds/info/inventory.csv`. Уникальность: (продукт, локация, статус) — при совпадении запись обновляется. Единица измерения подставляется из справочника продукта.

**Проверка:** страница «Остатки» в UI или `GET /api/v1/inventory`.
