"""
FastAPI application entry point for MES SaaS platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.db.session import Base
from backend.src.routes import (
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

# Create database tables (for development only, use migrations in production)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MES SaaS Platform API",
    description="Manufacturing Execution System API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_version="3.1.0",
)

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


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "MES SaaS Platform API", "version": "1.0.0"}
