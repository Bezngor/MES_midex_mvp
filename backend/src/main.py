"""
FastAPI application entry point for MES SaaS platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.db.session import Base
from backend.src.routes import health, orders, tasks

# Create database tables (for development only, use migrations in production)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MES SaaS Platform API",
    description="Manufacturing Execution System API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
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
app.include_router(health.router, tags=["health"])
app.include_router(orders.router, tags=["manufacturing-orders"])
app.include_router(tasks.router, tags=["production-tasks"])

# Placeholder for future routers
# app.include_router(work_centers.router, prefix="/api/v1", tags=["work-centers"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "MES SaaS Platform API", "version": "1.0.0"}
