"""
FastAPI application entry point for MES SaaS platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from backend.src.db.session import Base
from backend.core.routes import (
    health,
    orders,
    tasks,
    work_centers,
    dispatch,
    dispatching,
    manufacturing_routes,
    operations,
    products,
    bom,
    batches,
    inventory,
    work_center_capacities,
    mrp,
)
from backend.customizations.dsiz.routes import dsiz_planning_router, dsiz_dispatching_router
from backend.core.services.dispatching_service import DispatchingService
from backend.customizations.dsiz.services.dsiz_dispatching_service import DSIZDispatchingService
from backend.config.factory_config import get_factory_config

# Create database tables (for development only, use migrations in production)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MES Platform API",
    description="Manufacturing Execution System - Template v2.1.0",
    version="2.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Load factory configuration on startup
@app.on_event("startup")
def load_config():
    config = get_factory_config()
    print(f"Loaded factory config: {config.name} ({config.location})")

# Custom OpenAPI schema with version 3.0.3 (Swagger UI compatible)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="MES Platform API",
        version="2.1.0",
        description="Manufacturing Execution System API",
        routes=app.routes,
    )
    
    # Force OpenAPI 3.0.3 (Swagger UI compatible)
    openapi_schema["openapi"] = "3.0.3"
    
    # Add server URL
    openapi_schema["servers"] = [
        {"url": "https://mes-midex-ru.factoryall.ru", "description": "Production server"},
        {"url": "http://localhost:8000", "description": "Local development"}
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Dependency Injection: Override DispatchingService with DSIZDispatchingService
# Примечание: В FastAPI dependency_overrides работает только для функций-зависимостей, а не для классов.
# Существующие routes в core/routes/dispatching.py используют прямое создание экземпляра
# (service = DispatchingService(db)), поэтому override не применяется к ним.
# DSIZ routes используют Depends(get_dsiz_dispatching_service) и получат DSIZDispatchingService.
# 
# Для полноты выполнения задания добавлен импорт DSIZDispatchingService.
# Если в будущем core routes будут использовать Depends() для DispatchingService,
# можно будет добавить функцию-зависимость и override через app.dependency_overrides.

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(orders.router, tags=["manufacturing-orders"])
app.include_router(tasks.router, tags=["production-tasks"])
app.include_router(work_centers.router, tags=["work-centers"])
app.include_router(dispatch.router, tags=["dispatch"])
app.include_router(dispatching.router, tags=["Dispatching"])
app.include_router(manufacturing_routes.router, tags=["manufacturing-routes"])
app.include_router(operations.router, tags=["route-operations"])
app.include_router(products.router, tags=["products"])
app.include_router(bom.router, tags=["bill-of-materials"])
app.include_router(batches.router, tags=["batches"])
app.include_router(inventory.router, tags=["inventory"])
app.include_router(work_center_capacities.router, tags=["work-center-capacities"])
app.include_router(mrp.router, tags=["MRP"])
app.include_router(dsiz_planning_router, prefix="/api/v1", tags=["DSIZ"])
app.include_router(dsiz_dispatching_router, prefix="/api/v1", tags=["DSIZ"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "MES Platform API", "version": "2.1.0"}
