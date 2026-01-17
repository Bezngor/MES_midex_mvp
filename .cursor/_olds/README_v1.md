# MES SaaS Platform

Manufacturing Execution System (MES) SaaS platform for discrete manufacturing.

## Stack

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: React + TypeScript (to be implemented)
- **Orchestration**: n8n (to be implemented)
- **Analytics**: Power BI integration (to be implemented)

## Project Structure

```
MES_midex/
├── backend/              # Python FastAPI backend
│   ├── src/
│   │   ├── models/       # SQLAlchemy domain models
│   │   ├── schemas/      # Pydantic schemas/DTOs
│   │   ├── routes/       # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── db/           # Database session and migrations
│   │   ├── core/         # Settings and utilities
│   │   └── main.py       # FastAPI application entry point
│   ├── tests/            # Backend tests
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/             # React frontend (to be implemented)
├── n8n-workflows/        # n8n workflow exports (to be implemented)
├── docker-compose.yml    # Docker Compose configuration
└── docs/                 # Project documentation
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development without Docker)

### Running with Docker Compose

1. Clone the repository and navigate to the project directory.

2. Start the services:
   ```bash
   docker compose up
   ```
   Or using older Docker Compose syntax:
   ```bash
   docker-compose up
   ```

3. The services will be available at:
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/api/docs
   - **PostgreSQL**: localhost:5432

4. To stop the services:
   ```bash
   docker compose down
   ```

### Local Development (without Docker)

1. Install Python dependencies:
   ```bash
   cd backend
   pip install -e .
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database settings
   ```

3. Start PostgreSQL (or use Docker for database only):
   ```bash
   docker compose up postgres -d
   ```

4. Run the backend:
   ```bash
   cd backend
   uvicorn backend.src.main:app --reload
   ```

## Database Migrations

The project uses Alembic for database migrations. Migrations are located in `backend/src/db/migrations/`.

### Running Migrations

To run migrations (inside Docker container or local environment):

```bash
# From project root
cd backend
alembic upgrade head
```

To create a new migration:

```bash
cd backend
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

**Note**: Make sure the database is running before executing migrations. The migration scripts will automatically create all required tables, indexes, and constraints.

## API Endpoints

Base URL: `/api/v1`

### Health Check
- `GET /health` - API health status

More endpoints will be added as development progresses.

## 🚀 Production Deployment

See [DEPLOYMENT.md](./docs/DEPLOYMENT.md) for detailed production deployment instructions.

**Quick Start:**

```bash
# 1. Clone repository
git clone -b develop https://github.com/Bezngor/MES_midex.git
cd MES_midex

# 2. Configure environment
cp .env.example .env
nano .env  # Edit with production credentials

# 3. Deploy
docker-compose -f docker-compose.production.yml up -d

# 4. Run migrations
docker exec mes_backend alembic upgrade head
```

**Production Infrastructure:**
- **VPS**: Beget Ubuntu 22.04 (155.212.184.11)
- **Orchestration**: Dokploy (Docker-based PaaS)
- **Database**: Supabase PostgreSQL (supabase-db:5432)
- **Domain**: mes-midex-ru.factoryall.ru
- **SSL**: Traefik (managed by Dokploy)

For detailed architecture information, see [DOCKER_PRODUCTION.md](./docs/DOCKER_PRODUCTION.md).

## Development

See `.cursor/rules/` for development guidelines and architecture rules.

## License

[To be specified]
