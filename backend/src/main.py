"""
FastAPI application entry point for MES SaaS platform.
"""

import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
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
    validation,
    dev,
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
    print(f"CORS allowed origins: {_cors_origins}")

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

# Configure CORS (with credentials, "*" is not allowed by browsers — use explicit origins)
_dev_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
_cors_raw = os.getenv("CORS_ORIGINS", "").strip()
_cors_origins = [o.strip() for o in _cors_raw.split(",") if o.strip()] if _cors_raw else list(_dev_origins)
_env = (os.getenv("ENVIRONMENT") or "").strip().lower()
# В режиме разработки/теста или при незаданном ENVIRONMENT всегда разрешаем localhost (вариант 1 в TEST_RUN_GUIDE)
if _env in ("", "development", "dev", "test"):
    for o in _dev_origins:
        if o not in _cors_origins:
            _cors_origins.append(o)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


class ForceCORSHeadersMiddleware(BaseHTTPMiddleware):
    """Добавляет CORS-заголовки ко всем ответам с разрешённого origin (в т.ч. при ошибках и preflight)."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        origin = request.headers.get("origin")
        if origin and origin in _cors_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        return response


app.add_middleware(ForceCORSHeadersMiddleware)

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
# Роутер действий батчей (start/complete) — первым, чтобы /batches/start/{id} и /complete/{id} всегда находились
app.include_router(batches.router_actions, tags=["batches"])
app.include_router(batches.router, tags=["batches"])
app.include_router(inventory.router, tags=["inventory"])
app.include_router(work_center_capacities.router, tags=["work-center-capacities"])
app.include_router(mrp.router, tags=["MRP"])
app.include_router(validation.router, tags=["validation"])
app.include_router(dev.router)
app.include_router(dsiz_planning_router, prefix="/api/v1", tags=["DSIZ"])
app.include_router(dsiz_dispatching_router, prefix="/api/v1", tags=["DSIZ"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "MES Platform API", "version": "2.1.0"}
