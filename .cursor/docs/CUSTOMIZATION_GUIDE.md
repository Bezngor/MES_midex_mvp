# Customization Guide

This guide explains how to customize MES Platform for your factory without modifying core logic.

***

## Customization Layers

### Layer 1: Configuration (No Code)
Edit YAML files in `config/` directory.

### Layer 2: Business Logic (Python)
Override services in `backend/customizations/`.

### Layer 3: UI Components (React)
Add custom components in `frontend/src/customizations/`.

***

## Layer 1: Configuration

### Example: Change Planning Horizon

**File:** `config/factory_config.yaml`

```yaml
factory:
  planning:
    mrp_horizon_days: 60  # Change from 30 to 60 days
```

No code changes needed. Restart backend:

```bash
docker compose restart backend
```

### Example: Enable Shifts

**File:** `config/factory_config.yaml`

```yaml
factory:
  shifts:
    enabled: true
    config_file: "./config/shifts.yaml"
```

**File:** `config/shifts.yaml`

```yaml
shifts:
  - name: "Morning Shift"
    start_time: "06:00"
    end_time: "14:00"
    days: ["monday", "tuesday", "wednesday", "thursday", "friday"]
    capacity_multiplier: 1.0
```

***

## Layer 2: Business Logic

### Example: Custom Batch Rounding

**Create file:** `backend/customizations/custom_mrp_logic.py`

```python
"""Custom MRP logic for batch rounding"""
import math
from uuid import UUID
from backend.core.services.mrp_service import MRPService
from backend.core.models.product import Product

class CustomMRPService(MRPService):
    """Override MRP batch rounding logic"""
    
    def round_to_batch(self, product_id: UUID, net_requirement_kg: float) -> float:
        """
        Custom rounding logic:
        - BULK products: Round to nearest 100kg
        - RAW_MATERIAL: Round to nearest 50kg
        - Others: Use default logic
        """
        product = self.db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return super().round_to_batch(product_id, net_requirement_kg)
        
        # Custom logic for BULK products
        if product.product_type == "BULK":
            return math.ceil(net_requirement_kg / 100) * 100
        
        # Custom logic for RAW_MATERIAL
        if product.product_type == "RAW_MATERIAL":
            return math.ceil(net_requirement_kg / 50) * 50
        
        # Fallback to default
        return super().round_to_batch(product_id, net_requirement_kg)
```

**Register in:** `backend/src/main.py`

```python
from fastapi import FastAPI
from backend.customizations.custom_mrp_logic import CustomMRPService
from backend.core.services.mrp_service import MRPService

app = FastAPI(...)

# Override MRP service with custom implementation
def get_custom_mrp_service():
    return CustomMRPService(db=get_db())

app.dependency_overrides[MRPService] = get_custom_mrp_service
```

### Example: Custom Validation

**Create file:** `backend/customizations/custom_validation.py`

```python
"""Custom validation rules"""
from fastapi import HTTPException

def validate_hazmat_batch_size(product_code: str, quantity_kg: float):
    """
    Hazmat products cannot exceed 200kg per batch
    """
    if product_code.startswith("HAZMAT-") and quantity_kg > 200:
        raise HTTPException(
            status_code=400,
            detail="Hazmat products cannot exceed 200kg per batch (safety regulation)"
        )

def validate_cold_chain_product(product_code: str, location: str):
    """
    Cold chain products must be in refrigerated zones
    """
    REFRIGERATED_ZONES = ["COLD-01", "COLD-02", "FREEZER-01"]
    
    if product_code.startswith("COLD-") and location not in REFRIGERATED_ZONES:
        raise HTTPException(
            status_code=400,
            detail=f"Cold chain product must be stored in: {', '.join(REFRIGERATED_ZONES)}"
        )
```

**Use in routes:** `backend/core/routes/batches.py`

```python
from backend.customizations.custom_validation import validate_hazmat_batch_size

@router.post("/", response_model=BatchSchema)
def create_batch(payload: BatchCreate, db: Session = Depends(get_db)):
    # Custom validation
    validate_hazmat_batch_size(payload.product_code, payload.quantity_kg)
    
    # Rest of logic...
```

***

## Layer 3: UI Components

### Example: Custom Dashboard Widget

**Create file:** `frontend/src/customizations/FactoryKPI.tsx`

```typescript
import React from 'react';

export const FactoryKPI: React.FC = () => {
  return (
    <div className="bg-white shadow rounded-lg p-4">
      <h3 className="text-lg font-semibold mb-2">Factory KPIs</h3>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <p className="text-sm text-gray-600">OEE</p>
          <p className="text-2xl font-bold text-green-600">87%</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">On-Time Delivery</p>
          <p className="text-2xl font-bold text-blue-600">92%</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Scrap Rate</p>
          <p className="text-2xl font-bold text-red-600">3.2%</p>
        </div>
      </div>
    </div>
  );
};
```

**Use in:** `frontend/src/pages/Dashboard.tsx`

```typescript
import { FactoryKPI } from '../customizations/FactoryKPI';

export const Dashboard = () => {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      
      {/* Custom widget */}
      <FactoryKPI />
      
      {/* Existing dashboard content */}
      <OrderForm />
      <OrderList />
    </div>
  );
};
```

***

## Best Practices

### 1. Don't Modify Core Files
❌ **Bad:**
```python
# Editing backend/core/services/mrp_service.py directly
```

✅ **Good:**
```python
# Create backend/customizations/custom_mrp_logic.py
# Extend MRPService class
```

### 2. Use Configuration First
❌ **Bad:** Hardcoding values in Python

```python
HORIZON_DAYS = 30  # Hardcoded
```

✅ **Good:** Using configuration

```python
from backend.config.factory_config import get_factory_config

config = get_factory_config()
horizon_days = config.planning.mrp_horizon_days
```

### 3. Document Customizations
Always add comments explaining WHY you customized:

```python
def round_to_batch(self, product_id: UUID, net_requirement_kg: float) -> float:
    """
    Custom rounding for ACME Corp factory:
    - BULK products limited to 100kg batches due to mixer capacity
    - Regulation XYZ requires hazmat rounding to 50kg
    """
    # ... logic
```

### 4. Test Customizations
Create tests in `backend/tests/customizations/`:

```python
# tests/customizations/test_custom_mrp.py
def test_bulk_product_rounding():
    service = CustomMRPService(db)
    result = service.round_to_batch(bulk_product_id, 237.5)
    assert result == 300  # Rounded to nearest 100kg
```

***

## Troubleshooting

### Customization Not Applied

1. Check import in `main.py`
2. Verify dependency override
3. Restart backend: `docker compose restart backend`
4. Check logs: `docker compose logs backend`

### Configuration Not Loaded

1. Verify YAML syntax: `python -m yaml config/factory_config.yaml`
2. Check file path in `factory_config.py`
3. Check logs for "Loaded factory config" message

### Type Errors

Install dependencies:
```bash
cd backend
pip install pyyaml pydantic
```

***

## Examples Repository

See `examples/` directory for complete customization examples:
- `examples/pharmaceutical_factory/` — GMP compliance, serialization
- `examples/food_factory/` — HACCP, allergen tracking
- `examples/automotive_factory/` — JIT, kanban
