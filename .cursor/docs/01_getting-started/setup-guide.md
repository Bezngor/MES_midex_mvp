# Setup Guide - MES_midex

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15
- Docker & Docker Compose

## 1. Clone Repository

```bash
git clone https://github.com/Bezngor/MES_midex.git
cd MES_midex
```

## 2. Backend Setup

```shell
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
```

## 3. Frontend Setup

```shell
cd ../frontend
npm install
```

## 4. Environment Configuration

Copy and configure environment files:

```shell
cp .env.example .env
# Edit .env with your database credentials
```

## 5. Database Setup

```shell
# Using Docker
docker-compose up -d postgres

# Or use existing PostgreSQL
createdb mes_db
```

## 6. Run Migrations

```shell
cd backend
alembic upgrade head
```

## 7. Start Development

Terminal 1 - Backend:

```shell
cd backend
uvicorn src.main:app --reload --port 8000
```

Terminal 2 - Frontend:

```shell
cd frontend
npm run dev
```

Verify Setup

Open http://localhost:5173 (frontend) and http://localhost:8000/docs (API)


Next: Read Architecture Overview
