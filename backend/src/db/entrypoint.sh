#!/bin/bash
set -e

echo "🚀 DSIZ Deployment Entrypoint: Starting migrations..."

# Переходим в директорию с alembic.ini
cd /app

# Проверяем доступность БД (максимум 30 попыток, интервал 2 секунды)
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; then
        echo "✅ Database connection successful"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "⏳ Waiting for database... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ ERROR: Database not available after $MAX_RETRIES attempts"
    exit 1
fi

# Запускаем миграции Alembic
echo "📦 Running Alembic migrations..."
alembic -c /app/alembic.ini upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully"
else
    echo "❌ ERROR: Migrations failed"
    exit 1
fi

# Запускаем приложение с переданными аргументами
echo "🚀 Starting application: $@"
exec "$@"
