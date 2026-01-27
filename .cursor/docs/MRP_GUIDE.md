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
Create Bulk Order
bash
POST /api/v1/mrp/create-bulk-order
{
  "parent_order_id": "uuid-parent-order",  # Optional
  "bulk_product_id": "uuid-bulk-cream",
  "quantity_kg": 900,
  "due_date": "2026-01-21T12:00:00Z"
}
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