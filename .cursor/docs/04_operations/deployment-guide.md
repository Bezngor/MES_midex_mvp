# Deployment Guide

## Development Environment

```bash
# Start all services
docker-compose up -d

# Access:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - PostgreSQL: localhost:5432
```

## Production Deployment

**VPS Setup (gldkosfhmj)**

Path: /opt/mes-platform

```python
# SSH to server
ssh root@gldkosfhmj

# Navigate to project
cd /opt/mes-platform

# Pull latest changes
git pull origin main

# Build and start
docker-compose -f docker-compose.production.yml up -d --build
```

## Environment Variables

**Production (.env.production):**

```python
DATABASE_URL=postgresql://user:pass@postgres:5432/mes_db
JWT_SECRET_KEY=your-secret-key
SECRET_KEY=your-secret-key
```

## Database Migrations

```python
# Run migrations
cd backend
alembic upgrade head
```

## Health Checks

**Backend:**

curl http://localhost:8000/health

**Database:**

```python
docker exec mes_postgres pg_isready -U mes_user
```

## Backup Strategy

**Database Backup:**

```python
docker exec mes_postgres pg_dump -U mes_user mes_db > backup_$(date +%Y%m%d).sql
```

## Troubleshooting

**Container not starting:**

```python
docker-compose -f docker-compose.production.yml logs
```

**Database connection issues:**

• Check .env.production DATABASE_URL
• Verify postgres container is running
