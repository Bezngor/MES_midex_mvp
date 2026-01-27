"""add_ship_in_work_to_orderstatus

Revision ID: 20260114171052
Revises: 20260114000001
Create Date: 2026-01-14 17:10:52.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260114171052'
down_revision = '20260114000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Добавить значения SHIP и IN_WORK в enum orderstatus."""
    # Добавляем новые значения в enum orderstatus
    # Используем блок DO с обработкой исключений для совместимости со всеми версиями PostgreSQL
    op.execute("""
        DO $$ BEGIN
            -- Проверяем, существует ли значение 'SHIP' в enum
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumlabel = 'SHIP' 
                AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'orderstatus')
            ) THEN
                ALTER TYPE orderstatus ADD VALUE 'SHIP';
            END IF;
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            -- Проверяем, существует ли значение 'IN_WORK' в enum
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum 
                WHERE enumlabel = 'IN_WORK' 
                AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'orderstatus')
            ) THEN
                ALTER TYPE orderstatus ADD VALUE 'IN_WORK';
            END IF;
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)


def downgrade() -> None:
    """Откатить изменения: удалить значения SHIP и IN_WORK из enum orderstatus."""
    # В PostgreSQL нельзя напрямую удалить значение из enum
    # Нужно создать новый enum, обновить таблицы и удалить старый
    # Для упрощения оставляем значения в enum, но они не будут использоваться
    # Если нужно полное удаление, требуется более сложная миграция:
    # 1. Создать новый enum без SHIP и IN_WORK
    # 2. Обновить все таблицы на новый enum
    # 3. Удалить старый enum
    # 4. Переименовать новый enum в старый
    pass
