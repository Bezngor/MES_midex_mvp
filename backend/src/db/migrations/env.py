"""
Alembic environment configuration.

Фикс для production после core рефакторинга:
- Base импортируется из backend.src.db.session (НЕ из core.models!)
- Все модели импортируются из backend.core.models для регистрации в Base.metadata
"""

from logging.config import fileConfig
import os
import sys
from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context

# Add the project root directory to the path
# This allows imports like 'backend.src.db.session'
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)

# ✅ Base из backend.src.db.session (ТОЧНО!)
from backend.src.db.session import Base

# ✅ Импортируем ВСЕ модели из backend.core.models для регистрации в Base.metadata
from backend.core.models import (
    ManufacturingOrder,
    WorkCenter,
    ManufacturingRoute,
    RouteOperation,
    ProductionTask,
    GenealogyRecord,
    QualityInspection,
    Product,
    BillOfMaterial,
    Batch,
    InventoryBalance,
    WorkCenterCapacity,
)

# ✅ Импортируем DSIZ модели для регистрации в Base.metadata
from backend.customizations.dsiz.models import (
    DSIZWorkCenterMode,
    DSIZProductWorkCenterRouting,
    DSIZChangeoverMatrix,
    DSIZBaseRates,
    DSIZWorkforceRequirements,
)

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://mes_user:mes_password@localhost:5432/mes_db"
)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the SQLAlchemy URL from environment
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    Использует sqlalchemy.url из config (установлен из DATABASE_URL env).
    """
    # Используем engine_from_config с URL из config (установлен из DATABASE_URL)
    # Это стандартный подход Alembic, который правильно обрабатывает подключение
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
