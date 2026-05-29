# Multifolio

Monorepo with a FastAPI backend and Next.js 15 frontend.

## Quick Start

```bash
docker compose up
```

This starts all 5 services: `api` (port 8000), `frontend` (port 3000), `postgres` (port 5432), `redis` (port 6379), and `worker`.

## Services

| Service    | URL                        |
|------------|----------------------------|
| API        | http://localhost:8000      |
| API Docs   | http://localhost:8000/docs |
| Frontend   | http://localhost:3000      |
| Health     | http://localhost:8000/health |

## Local Development (without Docker)

### Backend

```bash
cd backend
cp .env.example .env   # fill in values
uv sync
uv run uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

## Stack

- **Backend**: FastAPI, SQLAlchemy 2 async, Alembic, Celery, Redis, PostgreSQL 16
- **Frontend**: Next.js 15 App Router, TypeScript, Tailwind CSS 4, shadcn/ui, Zustand
- **Infra**: Docker Compose, GitHub Actions CI
