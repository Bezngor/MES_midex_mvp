# Customization Guide

This directory contains factory-specific customizations that override core logic.

## How to Customize

### 1. Override MRP Logic

Create `custom_mrp_logic.py`:

```python
from backend.core.services.mrp_service import MRPService

class CustomMRPService(MRPService):
    """Custom MRP logic for your factory"""
    
    def round_to_batch(self, product_id: str, net_requirement_kg: float) -> float:
        """Custom batch rounding logic"""
        # Example: Round to nearest 100kg for BULK products
        product = self.db.query(Product).filter(Product.id == product_id).first()
        
        if product and product.product_code.startswith("BULK"):
            return math.ceil(net_requirement_kg / 100) * 100
        
        # Fallback to default
        return super().round_to_batch(product_id, net_requirement_kg)
```

Register in `main.py`:
```python
from backend.customizations.custom_mrp_logic import CustomMRPService
from backend.core.services.mrp_service import MRPService

# Override dependency
app.dependency_overrides[MRPService] = CustomMRPService
```

### 2. Add Custom Validation

Create `custom_validation.py`:

```python
from fastapi import HTTPException

def validate_batch_size(product_id: str, quantity_kg: float):
    """Custom validation for batch sizes"""
    # Example: Fragile products max 500kg
    if quantity_kg > 500:
        raise HTTPException(
            status_code=400,
            detail="Batch size cannot exceed 500kg"
        )
```

Use in routes:
```python
from backend.customizations.custom_validation import validate_batch_size

@router.post("/batches")
def create_batch(payload: BatchCreate):
    validate_batch_size(payload.product_id, payload.quantity_kg)
    # ... rest of logic
```

## Best Practices

1. **Don't modify `core/` files** — always extend in `customizations/`
2. **Use dependency injection** — override services via `app.dependency_overrides`
3. **Document your changes** — add comments explaining custom logic
4. **Test customizations** — create tests in `tests/customizations/`
