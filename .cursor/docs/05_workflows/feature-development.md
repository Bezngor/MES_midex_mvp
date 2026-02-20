# Feature Development Workflow

## Phase 1: Analysis (Q)

1. **Request Analysis**
   - Q analyzes requirements via GitHub API
   - Reviews existing code structure
   - Identifies affected components

2. **Prompt Generation**
   - Q creates detailed Cursor-ready prompt
   - Includes: context, requirements, code examples
   - Specifies: file paths, patterns, tests

## Phase 2: Implementation (Developer)

1. **Receive Prompt** from Q via Telegram
2. **Open Cursor IDE** with project
3. **Implement** following Q's specifications:
   - Create/modify files
   - Add type hints
   - Write tests
   - Update migrations (if needed)

4. **Local Testing**
   ```bash
   # Backend tests
   cd backend && pytest
   
   # Frontend build
   cd frontend && npm run build
```

5. **Git Commit & Push

```python
git add .
git commit -m "feat: description"
git push origin feature/branch-name
```

## Phase 3: Review (Q)

1. Webhook Triggered on push
2. Q performs automated code review via GitHub API
3. Feedback sent to Telegram
4. Iterate if needed
DSIZ Feature Template

For New DSIZ Features:

Models (customizations/dsiz/models/):

```python
class NewDSIZModel(Base):
    __tablename__ = "dsiz_new_table"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    # ... fields
```

Services (customizations/dsiz/services/):

```python
class NewDSIZService:
    def __init__(self, db: Session):
        self.db = db
    
    async def business_logic(self) -> Result:
        ...
```

Routes (customizations/dsiz/routes/):

```python
@router.post("/new-endpoint")
async def endpoint(
    service: NewDSIZService = Depends(get_new_service)
):
    return await service.business_logic()
```

Tests (tests/customizations/dsiz/):

```python
async def test_new_feature(db: Session):
    service = NewDSIZService(db)
    result = await service.business_logic()
    assert result.success
```


Last Updated: 2026-02-20