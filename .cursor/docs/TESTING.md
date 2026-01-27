# MES Platform Testing Guide

## Overview

This document describes the testing strategy and practices for the MES Platform.

---

## Testing Stack

- **Framework:** pytest 7.4.3
- **Coverage:** pytest-cov
- **Database:** SQLite (in-memory for tests)
- **Fixtures:** centralized in `conftest.py`

---

## Test Structure

backend/tests/
├── conftest.py # Shared fixtures
├── models/ # Unit tests for ORM models
│ ├── test_product.py
│ ├── test_bom.py
│ ├── test_batch.py
│ ├── test_inventory.py
│ └── test_work_center_capacity.py
└── api/ # Integration tests for API endpoints
├── test_products_api.py
├── test_bom_api.py
├── test_batches_api.py
├── test_inventory_api.py
└── test_work_center_capacities_api.py

text

---

## Running Tests

### Run all tests
```bash
cd backend
pytest tests/ -v
Run specific test file
bash
pytest tests/models/test_product.py -v
Run with coverage
bash
pytest tests/ --cov=app --cov-report=html
Open coverage report
bash
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
Test Statistics (Iteration 2.0)
Total Tests: 61

Passed: 60

Skipped: 1 (CASCADE DELETE in SQLite)

Failed: 0

Coverage: 80%+ for new code

Fixtures
Product Fixtures
sample_bulk_product — BULK product with batch parameters

sample_finished_good — FINISHED_GOOD product

sample_packaging — PACKAGING product

sample_raw_material — RAW_MATERIAL product

BOM Fixtures
sample_bom_fg_to_bulk — FG → BULK

sample_bom_fg_to_packaging — FG → PACKAGING

sample_bom_bulk_to_raw — BULK → RAW

Batch Fixtures
sample_batch — batch with PLANNED status

sample_batch_in_progress — batch with IN_PROGRESS status

Inventory Fixtures
sample_inventory_finished — FINISHED inventory

sample_inventory_semi_finished — SEMI_FINISHED inventory

WorkCenterCapacity Fixtures
sample_wc_capacity_tubing_cream — capacity for tubing machine

sample_wc_capacity_reactor_bulk — capacity for reactor

Testing Best Practices
1. Use AAA Pattern
python
def test_create_product(db_session):
    # Arrange
    product = Product(product_code="TEST", ...)
    
    # Act
    db_session.add(product)
    db_session.commit()
    
    # Assert
    assert product.id is not None
2. Test Constraints
python
def test_unique_constraint(db_session, sample_product):
    duplicate = Product(product_code=sample_product.product_code, ...)
    db_session.add(duplicate)
    
    with pytest.raises(IntegrityError):
        db_session.commit()
3. Test Relationships
python
def test_relationships(db_session, sample_bom):
    assert sample_bom.parent_product is not None
    assert sample_bom.child_product is not None
4. Test API Responses
python
def test_api_endpoint(client):
    response = client.post("/api/v1/products", json={...})
    
    assert response.status_code == 201
    assert response.json()["success"] is True
    assert response.json()["data"]["id"] is not None
Known Issues
SQLite Limitations
CASCADE DELETE test skipped in SQLite:

SQLite doesn't fully support ON DELETE CASCADE in the same way as PostgreSQL

Test: test_bom_cascade_delete is skipped in test environment

Works correctly in PostgreSQL (production)

Workaround:

python
@pytest.mark.skipif(
    os.getenv("TEST_DB") == "sqlite",
    reason="CASCADE DELETE not fully supported in SQLite"
)
def test_bom_cascade_delete(db_session, sample_bom):
    ...
CI/CD Integration (Future)
GitHub Actions Workflow
text
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/ --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
Changelog
2026-01-14 (Iteration 2.0):

Added 61 tests (60 passed, 1 skipped)

Unit tests for 5 new models

API tests for 5 new routers

14 new fixtures in conftest.py

Coverage: 80%+ for new code

2026-01-13 (MVP v1.0):

Initial 16 tests for core models

Basic API tests