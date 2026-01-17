# Docker Production Architecture

This document describes the Docker production deployment architecture for MES Platform v2.1.0.

## Architecture Overview

### Deployment Topology

```
┌─────────────────────────────────────────────────────────┐
│                    Dokploy Network                       │
│                    (External: dokploy)                  │
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   Frontend   │────────▶│   Backend    │             │
│  │  (nginx)     │  API    │  (gunicorn)  │             │
│  │  Port: 3000  │  Proxy  │  Port: 8000  │             │
│  └──────────────┘         └──────┬───────┘             │
│                                   │                      │
│                                   │ DATABASE_URL         │
│                                   ▼                      │
│                          ┌──────────────┐               │
│                          │   Supabase   │               │
│                          │  PostgreSQL  │               │
│                          │  Port: 5432  │               │
│                          └──────────────┘               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Docker Network

### Network Configuration

- **Network Name**: `dokploy` (external network)
- **Network Type**: Bridge
- **Purpose**: Connect MES services with Supabase database

### Service Communication

- **Frontend → Backend**: `http://mes_backend:8000` (internal Docker DNS)
- **Backend → Database**: `supabase-db:5432` (from DATABASE_URL)
- **External → Frontend**: `https://mes-midex-ru.factoryall.ru` (via Traefik)

## Container Architecture

### Backend Container

**Image**: `mes_backend` (built from `backend/Dockerfile.production`)

**Multi-Stage Build**:
1. **Builder Stage**: Installs dependencies and builds application
2. **Runtime Stage**: Minimal image with only runtime dependencies

**Key Features**:
- Python 3.11-slim base image
- Gunicorn with Uvicorn workers (4 workers)
- Non-root user (`appuser`) for security
- Health check endpoint: `/api/v1/health`
- Resource limits: 512MB memory, 0.5 CPU

**Ports**:
- `8000:8000` (HTTP API)

**Environment Variables**:
- Loaded from `.env` file via `env_file`
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key
- `CORS_ORIGINS`: Allowed origins for CORS

**Volumes**: None (stateless container)

### Frontend Container

**Image**: `mes_frontend` (built from `frontend/Dockerfile.production`)

**Multi-Stage Build**:
1. **Builder Stage**: npm install + npm run build
2. **Nginx Stage**: Serves static files from `dist/`

**Key Features**:
- Node.js 20-alpine for build stage
- Nginx alpine for runtime (minimal footprint)
- API proxy configuration for `/api/*` routes
- Static file caching (1 year)
- Gzip compression enabled
- Security headers (X-Frame-Options, etc.)

**Ports**:
- `3000:80` (HTTP web server)

**Build Arguments**:
- `VITE_API_URL`: API endpoint URL (injected at build time)

**Volumes**: None (static files baked into image)

## Volumes and Persistence

### No Persistent Volumes

The production deployment is **stateless**:
- Backend: No local file storage (all data in database)
- Frontend: Static files baked into Docker image
- Database: Managed by Supabase (external service)

### Temporary Storage

- Docker overlay filesystem for container filesystem
- No data persistence required between container restarts

## Resource Limits

### Backend Limits

```yaml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
    reservations:
      memory: 256M
      cpus: '0.25'
```

**Rationale**:
- 4 Gunicorn workers × ~64MB each = ~256MB base
- Additional memory for request handling and caching
- CPU limit prevents resource exhaustion

### Frontend Limits

```yaml
deploy:
  resources:
    limits:
      memory: 256M
      cpus: '0.25'
    reservations:
      memory: 128M
      cpus: '0.1'
```

**Rationale**:
- Nginx is lightweight (~10-20MB base)
- Static file serving requires minimal resources
- CPU limit sufficient for proxy operations

## Security Best Practices

### Container Security

1. **Non-Root User**: Backend runs as `appuser` (UID 1000)
2. **Minimal Base Images**: Alpine/slim variants reduce attack surface
3. **No Shell Access**: Containers don't expose shell by default
4. **Read-Only Filesystem**: Consider adding `read_only: true` for production

### Network Security

1. **Internal Communication**: Services communicate via Docker network
2. **No Exposed Database Ports**: Database only accessible within `dokploy` network
3. **CORS Configuration**: Restricted to production domain only
4. **HTTPS Only**: Traefik handles SSL termination

### Secrets Management

1. **Environment Variables**: Sensitive data in `.env` (not committed)
2. **No Hardcoded Secrets**: All secrets loaded from environment
3. **Secret Rotation**: Update `.env` and restart containers

## Health Checks

### Backend Health Check

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**Endpoint**: `GET /api/v1/health`
- Returns 200 OK if service is healthy
- Checks database connectivity
- Verifies application is responding

### Frontend Health Check

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:80"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```

**Endpoint**: `GET /health` (nginx custom endpoint)
- Returns 200 OK if nginx is serving content
- Verifies static files are accessible

## Restart Policies

### Configuration

```yaml
restart: unless-stopped
```

**Behavior**:
- Container restarts automatically on failure
- Container restarts after Docker daemon restart
- Container does NOT restart if manually stopped
- Prevents infinite restart loops on configuration errors

## Image Optimization

### Backend Image Size

**Target**: < 500MB

**Optimization Techniques**:
- Multi-stage build (builder artifacts not in final image)
- Python slim base image (~45MB)
- Only runtime dependencies in final stage
- No development tools in production image

### Frontend Image Size

**Target**: < 100MB

**Optimization Techniques**:
- Multi-stage build (Node.js not in final image)
- Nginx alpine base image (~23MB)
- Only built `dist/` files copied
- No source code or node_modules in final image

## Logging Strategy

### Log Output

- **Backend**: Gunicorn logs to stdout/stderr
- **Frontend**: Nginx access/error logs to stdout/stderr
- **Docker**: Captures all stdout/stderr

### Log Management

```bash
# View logs
docker logs mes_backend
docker logs mes_frontend

# Follow logs
docker logs -f mes_backend

# Log rotation (handled by Docker)
docker system prune --volumes
```

**Best Practices**:
- Use structured logging (JSON format)
- Aggregate logs to centralized system (ELK, Loki, etc.)
- Set log retention policies
- Monitor error rates

## Scaling Considerations

### Horizontal Scaling

**Backend**:
- Stateless design allows multiple instances
- Use load balancer (Traefik) to distribute traffic
- Database connection pooling handles concurrent connections

**Frontend**:
- Static files can be served from CDN
- Multiple nginx instances behind load balancer
- No session state to manage

### Vertical Scaling

**Resource Limits**:
- Increase `memory` and `cpus` limits in `docker-compose.production.yml`
- Monitor resource usage: `docker stats`
- Adjust Gunicorn workers based on CPU cores

## Monitoring

### Container Metrics

```bash
# Resource usage
docker stats mes_backend mes_frontend

# Container inspection
docker inspect mes_backend
docker inspect mes_frontend
```

### Application Metrics

- Health check endpoints for availability
- Application logs for errors and performance
- Database connection pool metrics
- API response times

## Troubleshooting

### Container Won't Start

1. Check logs: `docker logs mes_backend`
2. Verify environment variables: `docker exec mes_backend env`
3. Test health check: `curl http://localhost:8000/api/v1/health`

### High Memory Usage

1. Check current usage: `docker stats`
2. Review Gunicorn worker count
3. Check for memory leaks in application code
4. Increase memory limits if needed

### Network Issues

1. Verify network exists: `docker network ls`
2. Inspect network: `docker network inspect dokploy`
3. Test connectivity: `docker exec mes_backend ping supabase-db`

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Gunicorn Documentation](https://gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Dokploy Documentation](https://dokploy.com/docs)
