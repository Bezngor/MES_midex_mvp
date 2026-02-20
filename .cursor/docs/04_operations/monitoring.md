# Monitoring & Alerting

## Health Checks

### Backend Health Endpoint
```bash
# Check API health
curl http://localhost:8000/health

# Expected response
{"status": "healthy", "database": "connected"}
```

### Database Health

```bash
# PostgreSQL health
docker exec mes_postgres pg_isready -U mes_user

# Or via psql
psql $DATABASE_URL -c "SELECT 1"
```

### Docker Health

```bash
# Check all services
docker-compose ps

# Check logs
docker-compose logs --tail=100 backend
```

## Logging

### Backend Logs

```bash
# View logs
docker-compose logs -f backend

# Filter by level
docker-compose logs backend | grep ERROR
```

### PostgreSQL Logs

```bash
# Slow queries
docker-compose logs postgres | grep "duration:"
```

## Metrics to Monitor

### Database Metrics

• Connection count
• Slow queries (>1s)
• Disk usage
• Replication lag (if replica)
Application Metrics

• Response time (p95, p99)
• Error rate (4xx, 5xx)
• Request rate
• Memory usage
Business Metrics

• Manufacturing orders processed
• Production tasks completed
• DSIZ planning runs
• API endpoint usage
Alerting Rules

Critical (Page immediately)

• Database down
• API returning 500 errors
• Disk space >90%
Warning (Notify within 1 hour)

• Response time >2s
• Error rate >1%
• Memory usage >80%
Info (Daily summary)

• Request volume changes
• New error types
Monitoring Setup

### Basic (Docker)

```bash
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

### Log Aggregation

```bash
# Send logs to central system
docker-compose logs -f backend | logger -t mes-backend
```

## Troubleshooting Monitoring Issues

### No metrics visible

1. Check exporter is running
2. Verify network connectivity
3. Check firewall rules

### False positives

1. Adjust thresholds
2. Add hysteresis
3. Check seasonality

Last Updated: 2026-02-20