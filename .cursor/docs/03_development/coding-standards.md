# Coding Standards - MES_midex

## Backend (Python/FastAPI)

### Dependency Injection Pattern

**ALWAYS use FastAPI Depends():**

```python
# ✅ CORRECT
@router.post("/planning")
async def create_plan(
    mrp: DSIZMRPService = Depends(get_dsiz_mrp_service),
    db: Session = Depends(get_db)
):
    return await mrp.plan_production()

def get_dsiz_mrp_service(db: Session = Depends(get_db)) -> DSIZMRPService:
    return DSIZMRPService(db)

# ❌ WRONG - Direct instantiation
@router.post("/planning")
async def create_plan():
    db = SessionLocal()  # Don't do this!
    mrp = DSIZMRPService(db)  # Don't do this!
    return await mrp.plan_production()
```

### Type Hints

**All functions must have type hints:**

```python
async def get_manufacturing_order(
    order_id: UUID,
    service: ManufacturingOrderService = Depends(get_order_service)
) -> ManufacturingOrderResponse:
    ...
```

### Async/Await

**All database operations must be async:**

```python
# ✅ CORRECT
async def get_product(self, product_id: UUID) -> Product:
    result = await self.db.execute(select(Product).where(Product.id == product_id))
    return result.scalar_one_or_none()

# ❌ WRONG
def get_product(self, product_id: UUID) -> Product:  # Missing async
    result = self.db.query(Product).get(product_id)  # Not async
    return result
```

### Service Layer Pattern

**Business logic belongs in services, not routes:**

```python
# routes/planning.py
@router.post("/plan")
async def create_plan(request: PlanningRequest, service: PlanningService = Depends()):
    return await service.create_plan(request)  # Delegate to service

# services/planning.py
class PlanningService:
    async def create_plan(self, request: PlanningRequest) -> PlanningResponse:
        # All business logic here
        ...
```

## Frontend (React/TypeScript)

### Component Structure

**Use functional components with hooks:**

```python
// ✅ CORRECT
export const ProductionTable: React.FC<ProductionTableProps> = ({ orders }) => {
    const [loading, setLoading] = useState(false);
    const queryClient = useQueryClient();
    
    return (...)
}
```

### Type Safety

**Strict TypeScript:**

```python
// ✅ CORRECT
interface ManufacturingOrder {
    id: string;
    productId: string;
    quantity: number;
    status: OrderStatus;
}

// ❌ WRONG - Avoid 'any'
const order: any = fetchOrder();  // Don't do this!
```

### React Query Pattern

**Use React Query for server state:**

```python
// ✅ CORRECT
const { data: orders, isLoading } = useQuery({
    queryKey: ['manufacturing-orders'],
    queryFn: fetchOrders
});

const mutation = useMutation({
    mutationFn: createOrder,
    onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['manufacturing-orders'] });
    }
});
```

## Database (SQLAlchemy)

### Model Definition

**Use type annotations and relationships:**

```python
class ManufacturingOrder(Base):
    __tablename__ = "manufacturing_orders"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    
    product: Mapped["Product"] = relationship("Product", back_populates="orders")
```

### Migrations

**Always use Alembic for schema changes:**

```python
alembic revision --autogenerate -m "feat: add workforce_requirements table"
alembic upgrade head
```

## Testing

### Test Structure

**Mirror source structure in tests:**

tests/
├── unit/
│   ├── services/
│   └── models/
├── integration/
│   ├── api/
│   └── db/
└── fixtures/

### Test Pattern

```python
# ✅ CORRECT
async def test_create_manufacturing_order(db: AsyncSession):
    service = ManufacturingOrderService(db)
    order = await service.create_order(product_id=uuid4(), quantity=100)
    
    assert order.id is not None
    assert order.quantity == 100
    assert order.status == OrderStatus.PENDING
```

### Code Review Checklist

**Before submitting PR:**

• [ ] Type hints on all functions

MES Midex PM Agent, [20.02.2026 11:51]
• [ ] Docstrings for public APIs
• [ ] Async/await for DB operations
• [ ] Dependency injection used
• [ ] Tests added/modified
• [ ] No direct service instantiation
• [ ] No any types in TypeScript
• [ ] Migrations if schema changed


Last Updated: 2026-02-20