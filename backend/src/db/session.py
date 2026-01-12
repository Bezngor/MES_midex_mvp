"""
Database session management for PostgreSQL.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Get database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://mes_user:mes_password@localhost:5432/mes_db"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,
    max_overflow=20,
    echo=False,  # Set to True for SQL query logging (development only)
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()


def get_db():
    """
    Dependency function for FastAPI to get database session.
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
