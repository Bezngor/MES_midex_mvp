-- ============================================================================
-- DSIZ Seed Data
-- ============================================================================
-- Этот файл содержит начальные данные для DSIZ-специфичных таблиц.
-- Запускать после применения миграции: alembic upgrade head
-- 
-- Использование:
--   psql -U mes_user -d mes_db -f backend/src/db/migrations/seed_dsiz_data.sql
--   или через psycopg2 в Python скрипте
-- ============================================================================

-- ============================================================================
-- 1. Создание рабочих центров (если их нет)
-- ============================================================================
-- Примечание: Используйте существующие ID рабочих центров или создайте новые
-- Пример для DSIZ:
--   WC_REACTOR_MAIN - Реактор основной
--   WC_TUBE_LINE_1 - Линия тубировки 1
--   WC_AUTO_LIQUID_SOAP - Автоматическая линия розлива жидкого мыла

-- Создание рабочих центров DSIZ (если ещё нет — ON CONFLICT DO NOTHING)
INSERT INTO work_centers (id, name, resource_type, status, capacity_units_per_hour, batch_capacity_kg, cycles_per_shift, parallel_capacity, created_at, updated_at)
VALUES
    ('00000000-0000-0000-0000-000000000001'::uuid, 'WC_REACTOR_MAIN', 'MACHINE', 'AVAILABLE', 100.0, 2000.0, 2, 1, NOW(), NOW()),
    ('00000000-0000-0000-0000-000000000002'::uuid, 'WC_TUBE_LINE_1', 'MACHINE', 'AVAILABLE', 150.0, NULL, NULL, 1, NOW(), NOW()),
    ('00000000-0000-0000-0000-000000000003'::uuid, 'WC_AUTO_LIQUID_SOAP', 'MACHINE', 'AVAILABLE', 200.0, NULL, NULL, 4, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 2. Создание продуктов из bom_test.csv (примеры)
-- ============================================================================
-- Примечание: Используйте существующие продукты или создайте новые
-- SKU из CSV: 00-00000952, БП-00000087, 00-00000128, 00-00000129, БП-00000096, и т.д.

-- Создание продуктов DSIZ (если ещё нет — ON CONFLICT DO NOTHING)
INSERT INTO products (id, product_code, product_name, product_type, unit_of_measure, created_at, updated_at)
VALUES
    ('10000000-0000-0000-0000-000000000001'::uuid, '00-00000952', 'СЕВЕРЯНИН Паста для очистки с натур. абразивом, 200 мл, Экст, ФТ', 'FINISHED_GOOD', 'шт', NOW(), NOW()),
    ('10000000-0000-0000-0000-000000000002'::uuid, '00-00001055', 'СЕВЕРЯНИН Паста для очистки с натур. абразивом, 2 л, Канистра, Дозатор', 'FINISHED_GOOD', 'шт', NOW(), NOW()),
    ('10000000-0000-0000-0000-000000000003'::uuid, 'БП-00000087', 'GECO Крем регенерирующий, 100 мл, Лам, ФТ', 'FINISHED_GOOD', 'шт', NOW(), NOW()),
    ('10000000-0000-0000-0000-000000000004'::uuid, '00-00000128', 'GECO Крем гидрофильный, 100 мл, Лам, Винт', 'FINISHED_GOOD', 'шт', NOW(), NOW()),
    ('10000000-0000-0000-0000-000000000005'::uuid, '00-00000129', 'GECO Крем гидрофобный, 100 мл, Лам, Винт', 'FINISHED_GOOD', 'шт', NOW(), NOW()),
    ('10000000-0000-0000-0000-000000000006'::uuid, 'БП-00000096', 'GECO Крем универсальный, 100 мл, Лам, ФТ', 'FINISHED_GOOD', 'шт', NOW(), NOW()),
    ('10000000-0000-0000-0000-000000000007'::uuid, '00-00000023', 'GECO Мыло жидкое, 1 л, Флакон, Дозатор', 'FINISHED_GOOD', 'шт', NOW(), NOW()),
    ('10000000-0000-0000-0000-000000000008'::uuid, 'БП-00000111', 'GECO Мыло жидкое, 250 мл, Флакон, Дозатор', 'FINISHED_GOOD', 'шт', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- 3. dsiz_work_center_modes - Режимы реактора
-- ============================================================================
-- Режимы для WC_REACTOR_MAIN
INSERT INTO dsiz_work_center_modes (work_center_id, mode_name, min_load_kg, max_load_kg, cycle_duration_hours, max_cycles_per_shift, created_at)
SELECT 
    wc.id,
    'CREAM_MODE',
    500.0,
    1500.0,
    4,
    2,
    NOW()
FROM work_centers wc
WHERE wc.name = 'WC_REACTOR_MAIN'
ON CONFLICT (work_center_id, mode_name) DO NOTHING;

INSERT INTO dsiz_work_center_modes (work_center_id, mode_name, min_load_kg, max_load_kg, cycle_duration_hours, max_cycles_per_shift, created_at)
SELECT 
    wc.id,
    'PASTE_MODE',
    800.0,
    2000.0,
    5,
    2,
    NOW()
FROM work_centers wc
WHERE wc.name = 'WC_REACTOR_MAIN'
ON CONFLICT (work_center_id, mode_name) DO NOTHING;

-- ============================================================================
-- 4. dsiz_changeover_matrix - Матрица совместимости продуктов
-- ============================================================================
-- Группы совместимости: CREAM, PASTE, LIQUID, UNIVERSAL
INSERT INTO dsiz_changeover_matrix (from_compatibility_group, to_compatibility_group, status, setup_time_minutes)
VALUES
    ('CREAM', 'CREAM', 'COMPATIBLE', 0),
    ('PASTE', 'PASTE', 'COMPATIBLE', 0),
    ('LIQUID', 'LIQUID', 'COMPATIBLE', 0),
    ('UNIVERSAL', 'CREAM', 'COMPATIBLE', 0),
    ('UNIVERSAL', 'PASTE', 'COMPATIBLE', 0),
    ('UNIVERSAL', 'LIQUID', 'COMPATIBLE', 0),
    ('CREAM', 'PASTE', 'INCOMPATIBLE', 120),
    ('PASTE', 'CREAM', 'INCOMPATIBLE', 120),
    ('CREAM', 'LIQUID', 'INCOMPATIBLE', 90),
    ('LIQUID', 'CREAM', 'INCOMPATIBLE', 90),
    ('PASTE', 'LIQUID', 'INCOMPATIBLE', 150),
    ('LIQUID', 'PASTE', 'INCOMPATIBLE', 150)
ON CONFLICT (from_compatibility_group, to_compatibility_group) DO NOTHING;

-- ============================================================================
-- 5. dsiz_product_work_center_routing - Маршрутизация продуктов
-- ============================================================================
-- Примеры маршрутизации для продуктов из bom_test.csv
-- Кремы (GECO) → WC_TUBE_LINE_1 (приоритет 1 - авто)
-- Пасты (СЕВЕРЯНИН) → WC_TUBE_LINE_1 (приоритет 2 - полуавто)
-- Жидкое мыло → WC_AUTO_LIQUID_SOAP (приоритет 1, мин. количество 5000)

-- Кремы GECO на тубировку
INSERT INTO dsiz_product_work_center_routing (product_sku, work_center_id, is_allowed, min_quantity_for_wc, priority_order, created_at)
SELECT 
    p.product_code,
    wc.id,
    true,
    NULL,
    1,
    NOW()
FROM products p
CROSS JOIN work_centers wc
WHERE p.product_code IN ('БП-00000087', '00-00000128', '00-00000129', 'БП-00000096')
  AND wc.name = 'WC_TUBE_LINE_1'
ON CONFLICT (product_sku, work_center_id) DO NOTHING;

-- Пасты СЕВЕРЯНИН на тубировку (полуавто)
INSERT INTO dsiz_product_work_center_routing (product_sku, work_center_id, is_allowed, min_quantity_for_wc, priority_order, created_at)
SELECT 
    p.product_code,
    wc.id,
    true,
    NULL,
    2,
    NOW()
FROM products p
CROSS JOIN work_centers wc
WHERE p.product_code IN ('00-00000952', '00-00001055')
  AND wc.name = 'WC_TUBE_LINE_1'
ON CONFLICT (product_sku, work_center_id) DO NOTHING;

-- Жидкое мыло на авто-розлив
INSERT INTO dsiz_product_work_center_routing (product_sku, work_center_id, is_allowed, min_quantity_for_wc, priority_order, created_at)
SELECT 
    p.product_code,
    wc.id,
    true,
    5000,
    1,
    NOW()
FROM products p
CROSS JOIN work_centers wc
WHERE p.product_code IN ('00-00000023', 'БП-00000111')
  AND wc.name = 'WC_AUTO_LIQUID_SOAP'
ON CONFLICT (product_sku, work_center_id) DO NOTHING;

-- ============================================================================
-- 6. dsiz_base_rates - Базовые скорости операций
-- ============================================================================
-- Примеры базовых скоростей для продуктов на рабочих центрах
-- Кремы: 100 шт/час на тубировке
-- Пасты: 80 шт/час на тубировке
-- Жидкое мыло: 200 шт/час на авто-розливе

-- Кремы на тубировке
INSERT INTO dsiz_base_rates (product_sku, work_center_id, base_rate_units_per_hour, is_human_dependent)
SELECT 
    p.product_code,
    wc.id,
    100.0,
    false
FROM products p
CROSS JOIN work_centers wc
WHERE p.product_code IN ('БП-00000087', '00-00000128', '00-00000129', 'БП-00000096')
  AND wc.name = 'WC_TUBE_LINE_1'
ON CONFLICT DO NOTHING;

-- Пасты на тубировке
INSERT INTO dsiz_base_rates (product_sku, work_center_id, base_rate_units_per_hour, is_human_dependent)
SELECT 
    p.product_code,
    wc.id,
    80.0,
    true
FROM products p
CROSS JOIN work_centers wc
WHERE p.product_code IN ('00-00000952', '00-00001055')
  AND wc.name = 'WC_TUBE_LINE_1'
ON CONFLICT DO NOTHING;

-- Жидкое мыло на авто-розливе
INSERT INTO dsiz_base_rates (product_sku, work_center_id, base_rate_units_per_hour, is_human_dependent)
SELECT 
    p.product_code,
    wc.id,
    200.0,
    false
FROM products p
CROSS JOIN work_centers wc
WHERE p.product_code IN ('00-00000023', 'БП-00000111')
  AND wc.name = 'WC_AUTO_LIQUID_SOAP'
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 7. dsiz_workforce_requirements - Нормы укомплектованности персонала
-- ============================================================================
-- WC_REACTOR_MAIN: 1 OPERATOR (mandatory)
-- WC_TUBE_LINE_1: 1 OPERATOR + 1 PACKER (оба mandatory)
-- WC_AUTO_LIQUID_SOAP: 4 OPERATOR (min_degraded=3, factor=0.5)

-- Реактор: 1 оператор (обязательно)
INSERT INTO dsiz_workforce_requirements (work_center_id, role_name, required_count, is_mandatory, min_count_for_degraded_mode, degradation_factor)
SELECT 
    wc.id,
    'OPERATOR',
    1,
    true,
    NULL,
    NULL
FROM work_centers wc
WHERE wc.name = 'WC_REACTOR_MAIN'
ON CONFLICT (work_center_id, role_name) DO NOTHING;

-- Тубировка: оператор + упаковщик (оба обязательны)
INSERT INTO dsiz_workforce_requirements (work_center_id, role_name, required_count, is_mandatory, min_count_for_degraded_mode, degradation_factor)
SELECT 
    wc.id,
    'OPERATOR',
    1,
    true,
    NULL,
    NULL
FROM work_centers wc
WHERE wc.name = 'WC_TUBE_LINE_1'
ON CONFLICT (work_center_id, role_name) DO NOTHING;

INSERT INTO dsiz_workforce_requirements (work_center_id, role_name, required_count, is_mandatory, min_count_for_degraded_mode, degradation_factor)
SELECT 
    wc.id,
    'PACKER',
    1,
    true,
    NULL,
    NULL
FROM work_centers wc
WHERE wc.name = 'WC_TUBE_LINE_1'
ON CONFLICT (work_center_id, role_name) DO NOTHING;

-- Авто-розлив: 4 оператора (3=0.5 rate)
INSERT INTO dsiz_workforce_requirements (work_center_id, role_name, required_count, is_mandatory, min_count_for_degraded_mode, degradation_factor)
SELECT 
    wc.id,
    'OPERATOR',
    4,
    false,
    3,
    0.5
FROM work_centers wc
WHERE wc.name = 'WC_AUTO_LIQUID_SOAP'
ON CONFLICT (work_center_id, role_name) DO NOTHING;

-- ============================================================================
-- Проверка данных
-- ============================================================================
-- Раскомментируйте для проверки вставленных данных:
/*
SELECT 'Work Center Modes' as table_name, COUNT(*) as count FROM dsiz_work_center_modes
UNION ALL
SELECT 'Changeover Matrix', COUNT(*) FROM dsiz_changeover_matrix
UNION ALL
SELECT 'Product Routing', COUNT(*) FROM dsiz_product_work_center_routing
UNION ALL
SELECT 'Base Rates', COUNT(*) FROM dsiz_base_rates
UNION ALL
SELECT 'Workforce Requirements', COUNT(*) FROM dsiz_workforce_requirements;
*/
