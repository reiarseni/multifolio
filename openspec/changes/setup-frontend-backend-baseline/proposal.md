## Why

Multifolio es un proyecto greenfield sin ningún código. Para construir cualquier feature del dominio se necesita una base estructural funcional: monorepo organizado, servicios contenerizados, stack verificado end-to-end y CI que garantice calidad desde el primer commit.

## What Changes

- Inicialización del monorepo con `/backend` (FastAPI + UV) y `/frontend` (Next.js 15 App Router + TypeScript)
- Docker Compose con 5 servicios: `api`, `frontend`, `postgres`, `redis`, `worker`
- FastAPI con endpoint `GET /health` y arranque verificado
- Next.js con página raíz funcional y routing base del App Router
- Modelo `User` con Alembic; auto-migración al arrancar el contenedor `api`
- Autenticación JWT: access token en memoria del cliente, refresh token en httpOnly cookie
- Celery worker configurado con cola `default` única
- GitHub Actions CI: lint + test + build en cada PR para backend y frontend
- Archivos de entorno base (`.env.example`) para backend y frontend

## Capabilities

### New Capabilities

- `project-scaffold`: Estructura de directorios del monorepo, gestores de dependencias (UV, npm/pnpm), archivos de configuración de linting (Ruff, ESLint, Prettier) y tipado estricto
- `docker-dev-environment`: Docker Compose para desarrollo local con los 5 servicios requeridos por la spec; healthchecks y dependencias entre servicios
- `backend-app-skeleton`: FastAPI inicializado con estructura de módulos (routers, models, schemas, services), Alembic configurado, Pydantic v2 settings
- `frontend-app-skeleton`: Next.js 15 con App Router, Tailwind CSS 4, shadcn/ui inicializado, Zustand store base, React Hook Form + Zod configurados
- `user-auth`: Modelo User, endpoints de registro/login/logout/refresh, JWT con access token + refresh token en httpOnly cookie
- `ci-pipeline`: GitHub Actions con jobs de lint, test y build separados por workspace, corriendo en cada PR

### Modified Capabilities

<!-- ninguna — proyecto greenfield -->

## Impact

- **Nuevo código**: `/backend/` y `/frontend/` completos desde cero
- **Infraestructura**: `docker-compose.yml` y `docker-compose.override.yml` (dev)
- **CI**: `.github/workflows/backend.yml` y `.github/workflows/frontend.yml`
- **Dependencias externas**: PostgreSQL 16, Redis 7, Python 3.12, Node.js LTS
- **Seguridad**: CORS configurado con `allow_credentials=True` y origins explícitos desde el día uno para soportar httpOnly cookies cross-origin
