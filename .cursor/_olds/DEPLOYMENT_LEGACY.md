# Production Deployment Guide

This guide covers the production deployment of MES Platform v2.1.0 on Beget VPS with Dokploy.

## Prerequisites

### Infrastructure Requirements

- **VPS**: Beget Ubuntu 22.04 (155.212.184.11)
- **Orchestration**: Dokploy (Docker-based PaaS)
- **Database**: Supabase PostgreSQL (deployed in Dokploy)
- **Domain**: mes-midex-ru.factoryall.ru (A-record: 155.212.184.11)
- **Docker Network**: `dokploy` (external network)

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Access to Dokploy dashboard
- SSH access to VPS (if manual deployment)

## Environment Setup

### 1. Clone Repository

```bash
git clone -b develop https://github.com/Bezngor/MES_midex.git
cd MES_midex
```

### 2. Configure Environment Variables

Copy the example environment file and edit it with production credentials:

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

**Required Variables:**

```bash
# Database (Supabase в Dokploy)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@supabase-db:5432/postgres

# Security (generate with: openssl rand -hex 32)
SECRET_KEY=your-generated-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production
DEBUG=False

# CORS
CORS_ORIGINS=https://mes-midex-ru.factoryall.ru,http://mes-midex-ru.factoryall.ru

# API
API_V1_PREFIX=/api/v1
PROJECT_NAME=MES Platform Production
```

**Important Security Notes:**

- Never commit `.env` file to version control
- Use strong, randomly generated `SECRET_KEY`
- Verify `DATABASE_URL` points to correct Supabase instance
- Ensure `CORS_ORIGINS` matches your production domain

### 3. Verify Docker Network

Ensure the `dokploy` network exists:

```bash
docker network ls | grep dokploy
```

If it doesn't exist, create it:

```bash
docker network create dokploy
```

## Building and Running

### Build Production Images

```bash
docker-compose -f docker-compose.production.yml build
```

### Start Services

```bash
docker-compose -f docker-compose.production.yml up -d
```

### Verify Services

Check that all services are running:

```bash
docker-compose -f docker-compose.production.yml ps
```

Expected output:
```
NAME            IMAGE                    STATUS
mes_backend     mes_midex_backend       Up (healthy)
mes_frontend    mes_midex_frontend      Up (healthy)
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Backend only
docker-compose -f docker-compose.production.yml logs -f backend

# Frontend only
docker-compose -f docker-compose.production.yml logs -f frontend
```

## Database Migrations

### Run Migrations

After starting the backend service, run Alembic migrations:

```bash
docker exec mes_backend alembic upgrade head
```

### Verify Migration Status

```bash
docker exec mes_backend alembic current
```

### Create New Migration (if needed)

```bash
docker exec -it mes_backend alembic revision --autogenerate -m "description of changes"
docker exec mes_backend alembic upgrade head
```

## SSL/HTTPS Setup

### Using Traefik (Dokploy)

Dokploy uses Traefik for automatic SSL certificate management. Configure in Dokploy dashboard:

1. Navigate to your application in Dokploy
2. Enable Traefik integration
3. Set domain: `mes-midex-ru.factoryall.ru`
4. Traefik will automatically:
   - Obtain Let's Encrypt certificate
   - Configure HTTPS redirect
   - Handle SSL termination

### Manual Traefik Labels (if needed)

If using docker-compose directly with Traefik, add labels:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.mes-frontend.rule=Host(`mes-midex-ru.factoryall.ru`)"
  - "traefik.http.routers.mes-frontend.entrypoints=websecure"
  - "traefik.http.routers.mes-frontend.tls.certresolver=letsencrypt"
```

## Monitoring and Logs

### Health Checks

Services include health checks:

- **Backend**: `GET /api/v1/health`
- **Frontend**: `GET /health`

Check health status:

```bash
docker inspect mes_backend | grep -A 10 Health
docker inspect mes_frontend | grep -A 10 Health
```

### Application Logs

```bash
# Real-time logs
docker logs -f mes_backend
docker logs -f mes_frontend

# Last 100 lines
docker logs --tail 100 mes_backend
```

### Resource Usage

```bash
docker stats mes_backend mes_frontend
```

## Troubleshooting

### Backend Won't Start

1. **Check DATABASE_URL**:
   ```bash
   docker exec mes_backend env | grep DATABASE_URL
   ```

2. **Verify database connectivity**:
   ```bash
   docker exec mes_backend psql $DATABASE_URL -c "SELECT 1;"
   ```

3. **Check logs**:
   ```bash
   docker logs mes_backend
   ```

### Frontend Shows 502 Bad Gateway

1. **Verify backend is running**:
   ```bash
   docker ps | grep mes_backend
   ```

2. **Check nginx configuration**:
   ```bash
   docker exec mes_frontend nginx -t
   ```

3. **Test API connectivity from frontend**:
   ```bash
   docker exec mes_frontend wget -O- http://mes_backend:8000/api/v1/health
   ```

### Database Connection Issues

1. **Verify Supabase is accessible**:
   ```bash
   docker exec mes_backend ping -c 3 supabase-db
   ```

2. **Check network connectivity**:
   ```bash
   docker network inspect dokploy
   ```

3. **Verify DATABASE_URL format**:
   - Format: `postgresql://user:password@host:port/database`
   - Ensure host matches Supabase service name in Dokploy

### Port Conflicts

If ports 8000 or 3000 are already in use:

1. **Find process using port**:
   ```bash
   sudo lsof -i :8000
   sudo lsof -i :3000
   ```

2. **Modify docker-compose.production.yml**:
   ```yaml
   ports:
     - "8001:8000"  # Change host port
   ```

### Out of Memory

If containers are killed due to memory:

1. **Check current limits**:
   ```bash
   docker stats --no-stream
   ```

2. **Increase limits in docker-compose.production.yml**:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 1G  # Increase as needed
   ```

## Updating the Application

### Pull Latest Code

```bash
git pull origin develop
```

### Rebuild and Restart

```bash
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml build --no-cache
docker-compose -f docker-compose.production.yml up -d
docker exec mes_backend alembic upgrade head
```

### Rollback

If issues occur after update:

```bash
# Stop services
docker-compose -f docker-compose.production.yml down

# Checkout previous version
git checkout <previous-commit-hash>

# Rebuild and restart
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker exec supabase-db pg_dump -U postgres postgres > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker exec -i supabase-db psql -U postgres postgres < backup_YYYYMMDD_HHMMSS.sql
```

### Application Data

Application is stateless; no persistent data to backup beyond database.

## Security Best Practices

1. **Environment Variables**: Never commit `.env` files
2. **Secrets**: Use Dokploy secrets management for sensitive data
3. **Network**: Use Docker networks to isolate services
4. **Updates**: Keep Docker images and dependencies updated
5. **Monitoring**: Set up log aggregation and monitoring
6. **SSL**: Always use HTTPS in production (handled by Traefik)

## Support

For issues or questions:
- Check logs: `docker logs mes_backend` or `docker logs mes_frontend`
- Review [DOCKER_PRODUCTION.md](./DOCKER_PRODUCTION.md) for architecture details
- Consult [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
