# Debugging Guide

## Backend Debugging

### Common Issues

#### Database Connection Errors

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check connection string
cat backend/.env | grep DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

#### FastAPI Startup Errors

```bash
# Run with verbose output
cd backend
uvicorn src.main:app --reload --log-level debug

# Check for import errors
python -c "from src.main import app"
```

#### Alembic Migration Errors

```bash
# Check current revision
cd backend
alembic current

# Check history
alembic history

# If stuck, mark specific revision
alembic stamp <revision_id>
```

### Logging Configuration

#### Backend (FastAPI):

```bash
# Add to your endpoint for debugging
import logging
logger = logging.getLogger(__name__)

@router.get("/debug")
async def debug_endpoint():
    logger.debug("Debug endpoint called")
    return {"status": "ok"}
```

#### VS Code Debugging

launch.json:

```bash
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["src.main:app", "--reload"],
            "jinja": true
        }
    ]
}
```

### Frontend Debugging

#### React DevTools

• Install browser extension
• Open DevTools → Components tab
• Inspect props and state
Common React Issues

Infinite re-renders:

```bash
// Check dependency arrays
useEffect(() => {
    fetchData();
}, []); // Empty array = run once

// Missing dependency
useEffect(() => {
    fetchData(id);
}, [id]); // Add all dependencies
```

#### Network Debugging

Check API calls:

1. Open DevTools → Network tab
2. Filter by "Fetch/XHR"
3. Check request/response
Console Debugging

```bash
// Log with context
console.log('User data:', user);

// Log API response
const data = await fetchUser();
console.log('API response:', data);
```

### Database Debugging

#### Query Performance

```bash
-- Check slow queries
SELECT query, calls, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

#### Connection Issues

```bash
# Check active connections
psql -c "SELECT count(*) FROM pg_stat_activity;"

# Check locks
psql -c "SELECT * FROM pg_locks WHERE NOT granted;"
```

### Docker Debugging

#### Container Issues

```bash
# Check logs
docker-compose logs backend
docker-compose logs postgres

# Check container status
docker-compose ps

# Restart services
docker-compose restart backend
```

#### Volume Issues

```bash
# Check volumes
docker volume ls

# Clean up (WARNING: deletes data)
docker-compose down -v
```

## Common Error Messages

| Error                      | Cause                | Solution             |
| -------------------------- | -------------------- | -------------------- |
| Connection refused         | Service not running  | docker-compose up -d |
| Module not found           | Missing dependency   | pip install -e .     |
| Alembic revision not found | Database out of sync | alembic upgrade head |
| CORS error                 | Missing CORS config  | Check CORSMiddleware |

## Getting Help

1. Check this guide first
2. Review Troubleshooting
3. Check GitHub Issues (https://github.com/Bezngor/MES_midex/issues)
4. Ask Q (mention error message + context)

Last Updated: 2026-02-20