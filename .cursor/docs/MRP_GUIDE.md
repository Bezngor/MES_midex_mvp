# MRP (Material Requirements Planning) Guide

## Overview

MRP module calculates material requirements based on customer orders and available inventory.

---

## Core Concepts

### 1. Order Consolidation
- Groups orders by product
- Calculates priorities based on due dates
- Determines production quantities

**Priority Rules:**
- `<7 days` → URGENT
- `7-14 days` → HIGH
- `14-30 days` → NORMAL
- `>30 days` → LOW

---

### 2. BOM Explosion
- Recursively walks Bill of Materials tree
- Calculates component requirements
- Supports multi-level BOMs (FG → BULK → RAW)

**Example:**
FG "Cream 100ml" (10,000 pcs)
├── BULK "Cream Mass" (900 kg) [10,000 × 0.09 kg]
│ └── RAW "Glycerin" (135 kg) [900 × 0.15 kg]
└── PACKAGING "Tube 100ml" (10,000 pcs) [10,000 × 1]

text

---

### 3. Net Requirement Calculation
- **Net = Gross - Available**
- Only FINISHED inventory counted
- SEMI_FINISHED inventory excluded

---

### 4. Batch Rounding
- Rounds UP to batch multiples
- Ensures `>= min_batch_size_kg`
- Uses `batch_size_step_kg` for rounding

**Example:**
Requirement: 1200 kg
min_batch: 500 kg
step: 1000 kg
Result: 2000 kg (2 batches)

text

---

## API Usage

### Consolidate Orders
```bash
POST /api/v1/mrp/consolidate
{
  "horizon_days": 30
}
Explode BOM
bash
POST /api/v1/mrp/explode-bom
{
  "product_id": "uuid-fg-cream",
  "quantity": 10000
}
Calculate Net Requirement
bash
POST /api/v1/mrp/net-requirement
{
  "product_id": "uuid-bulk-cream",
  "gross_requirement": 900
}
Create Bulk Order (контракт для Swagger)

**Метод и путь:** `POST /api/v1/mrp/create-bulk-order`

**Тело запроса (JSON):**

| Поле | Тип | Обязательное | Описание |
|------|-----|--------------|----------|
| `bulk_product_id` | UUID | да | UUID **продукта** типа BULK (масса), не UUID заказа |
| `quantity_kg` | number | да | Нетто-потребность в кг (будет округлена до батча) |
| `due_date` | string (ISO 8601) | да | Крайний срок выполнения заказа |
| `parent_order_id` | UUID | нет | Родительский заказ (для связки с заказом ГП) |

**Пример запроса:**
```json
{
  "bulk_product_id": "9b7ae0fc-51f3-49d3-baab-1776381ed989",
  "quantity_kg": 1200,
  "due_date": "2026-02-15T12:00:00Z"
}
```
С опциональным родителем (подставьте реальный UUID заказа из списка заказов; иначе поле не передавайте):
```json
{
  "parent_order_id": "171802b2-d48c-4a46-8cef-e6c01e9e6065",
  "bulk_product_id": "9b7ae0fc-51f3-49d3-baab-1776381ed989",
  "quantity_kg": 1200,
  "due_date": "2026-02-15T12:00:00Z"
}
```
**Важно:** `parent_order_id` должен быть валидным UUID (например, `id` из GET заказов). Нельзя подставлять текст вроде `"uuid-родительского-заказа"` — будет ошибка валидации.

**Ответ 200 (success: true):**

| Поле | Описание |
|------|----------|
| `data.order` | Созданный производственный заказ |
| `data.order.id` | UUID заказа |
| `data.order.order_number` | Номер вида `BULK-YYYYMMDD-NNNN` |
| `data.order.product_id` | UUID продукта (BULK) |
| `data.order.quantity` | Количество после округления (= rounded_quantity) |
| `data.order.status` | `PLANNED` |
| `data.order.order_type` | `INTERNAL_BULK` |
| `data.order.parent_order_id` | UUID родителя или null |
| `data.order.due_date` | Крайний срок |
| `data.rounded_quantity` | Количество после округления до батча (≥ quantity_kg) |
| `data.original_quantity` | Переданное quantity_kg |

**Пример ответа:**
```json
{
  "success": true,
  "data": {
    "order": {
      "id": "uuid-заказа",
      "order_number": "BULK-20260215-0001",
      "product_id": "9b7ae0fc-51f3-49d3-baab-1776381ed989",
      "quantity": 2000,
      "status": "PLANNED",
      "order_type": "INTERNAL_BULK",
      "parent_order_id": null,
      "due_date": "2026-02-15T12:00:00Z"
    },
    "rounded_quantity": 2000,
    "original_quantity": 1200
  }
}
```

**Округление до батча:**
- Продукт должен быть типа **BULK** и иметь `min_batch_size_kg`, `batch_size_step_kg`.
- `rounded_quantity` = округление **вверх** до кратности `batch_size_step_kg`, но не меньше `min_batch_size_kg`.
- Пример: quantity_kg=1200, step=1000 → 2000; quantity_kg=500, min=1000 → 1000.
- Если в конфиге отключено batch_rounding или у продукта нет step — возвращается quantity_kg без округления.

**Ошибки:**
- **400** — продукт не найден, не BULK, или нет batch_size_step_kg (сообщение в `detail`).
- **500** — внутренняя ошибка.

Business Rules
Only SHIP orders are consolidated (IN_WORK orders planned for future iterations)

FINISHED inventory is counted, SEMI_FINISHED is not

Batch rounding always rounds UP (never down)

Circular BOM protection: max 10 levels deep

INTERNAL_BULK orders are created with order_type=INTERNAL_BULK

Testing
Run MRP tests:

bash
pytest tests/services/test_mrp_service.py -v
pytest tests/api/test_mrp_api.py -v
Known Limitations (MVP v2.0)
❌ No capacity checks in consolidation

❌ No lead time offset for dependent orders

❌ No changeover time consideration

❌ No multi-site planning

These will be addressed in Iteration 2.1+.