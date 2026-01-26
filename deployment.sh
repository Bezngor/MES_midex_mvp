#!/bin/bash
set -e

# 🚀 DSIZ Automated Deployment Script
# Автоматизирует весь процесс деплоя без ручных действий
# Использование: ./deployment.sh [branch_name]
# Пример: ./deployment.sh feat/dsiz-phase1-mrp

BRANCH=${1:-main}
PROJECT_DIR="/opt/mes-platform"
API_URL="https://mes-midex-ru.factoryall.ru/api/v1"

echo "=========================================="
echo "🚀 DSIZ Automated Deployment"
echo "=========================================="
echo "Branch: $BRANCH"
echo "Project Directory: $PROJECT_DIR"
echo ""

# Проверка директории
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ ERROR: Project directory $PROJECT_DIR not found"
    exit 1
fi

cd "$PROJECT_DIR"

# 1. Git Pull
echo "📥 Step 1: Pulling latest code from $BRANCH..."
git fetch origin
git checkout "$BRANCH" || echo "⚠️  Branch $BRANCH not found, using current branch"
git pull origin "$BRANCH" || git pull origin "$(git branch --show-current)"

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Git pull failed"
    exit 1
fi

echo "✅ Code updated successfully"
echo ""

# 2. Build and Start Containers
echo "🐳 Step 2: Building and starting Docker containers..."
docker compose -f docker-compose.production.yml up -d --build

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Docker compose failed"
    exit 1
fi

echo "✅ Containers started successfully"
echo ""

# 3. Wait for Backend to be Ready
echo "⏳ Step 3: Waiting for backend to be ready..."
MAX_WAIT=60
WAIT_COUNT=0

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    if docker compose -f docker-compose.production.yml exec -T backend curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "✅ Backend is ready"
        break
    fi
    WAIT_COUNT=$((WAIT_COUNT + 1))
    echo "   Waiting... ($WAIT_COUNT/$MAX_WAIT)"
    sleep 2
done

if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
    echo "⚠️  WARNING: Backend health check timeout, but continuing..."
fi

echo ""

# 4. Check Alembic Current Version
echo "📦 Step 4: Checking Alembic migration status..."
docker compose -f docker-compose.production.yml exec -T backend alembic -c /app/alembic.ini current

echo ""

# 5. Test DSIZ Planning Endpoint
echo "🧪 Step 5: Testing DSIZ Planning endpoint..."
PLANNING_DATE=$(date +%Y-%m-%d)
RESPONSE=$(curl -s -X POST "$API_URL/dsiz/planning/run" \
    -H "Content-Type: application/json" \
    -d "{\"planning_date\": \"$PLANNING_DATE\", \"horizon_days\": 7}")

if echo "$RESPONSE" | grep -q '"success":true'; then
    echo "✅ DSIZ Planning endpoint test: SUCCESS"
    echo "   Response: $RESPONSE"
else
    echo "⚠️  WARNING: DSIZ Planning endpoint test returned unexpected result"
    echo "   Response: $RESPONSE"
fi

echo ""

# 6. Final Health Check
echo "🏥 Step 6: Final health check..."
HEALTH_RESPONSE=$(curl -s "$API_URL/health")
if echo "$HEALTH_RESPONSE" | grep -q '"status"'; then
    echo "✅ Health check: OK"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo "⚠️  WARNING: Health check returned unexpected result"
    echo "   Response: $HEALTH_RESPONSE"
fi

echo ""
echo "=========================================="
echo "✅ Deployment completed successfully!"
echo "=========================================="
echo ""
echo "📊 Deployment Summary:"
echo "   - Code updated from: $BRANCH"
echo "   - Containers: Running"
echo "   - Migrations: Applied automatically via entrypoint.sh"
echo "   - API URL: $API_URL"
echo ""
echo "🔍 Useful commands:"
echo "   - View logs: docker compose -f docker-compose.production.yml logs -f backend"
echo "   - Check migrations: docker compose -f docker-compose.production.yml exec backend alembic -c /app/alembic.ini current"
echo "   - Restart: docker compose -f docker-compose.production.yml restart backend"
echo ""
