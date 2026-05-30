## 1. Monorepo scaffold y configuración raíz

- [x] 1.1 Crear `.gitignore` raíz con entradas para `.env`, `__pycache__`, `.next`, `node_modules`, `.venv`
- [x] 1.2 Crear `README.md` raíz con instrucciones de inicio rápido (`docker compose up`)
- [x] 1.3 Actualizar `openspec/config.yaml` con contexto del proyecto (stack, convenciones)

## 2. Scaffold del backend

- [x] 2.1 Inicializar `/backend` con `uv init` y configurar `pyproject.toml` con nombre `multifolio-backend`, Python 3.12+
- [x] 2.2 Agregar dependencias de producción: `fastapi`, `uvicorn[standard]`, `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `pydantic-settings`, `pyjwt`, `passlib[bcrypt]`, `celery[redis]`, `redis`
- [x] 2.3 Agregar dependencias de desarrollo: `ruff`, `pytest`, `pytest-asyncio`, `httpx`, `pytest-cov`
- [x] 2.4 Configurar Ruff en `pyproject.toml`: reglas `E`, `F`, `I`, `UP`; line-length 100; target Python 3.12
- [x] 2.5 Crear estructura de directorios: `src/app/{routers,models,schemas,services,core,db,worker}/__init__.py`
- [x] 2.6 Crear `/backend/.env.example` con todas las variables requeridas (ver spec `project-scaffold`)
- [x] 2.7 Configurar `pytest.ini` o sección `[tool.pytest.ini_options]` en `pyproject.toml` con `asyncio_mode = "auto"`

## 3. Aplicación FastAPI base

- [x] 3.1 Crear `src/app/core/config.py` con clase `Settings` (Pydantic BaseSettings) que cargue todas las variables de entorno
- [x] 3.2 Crear `src/app/db/session.py` con el engine SQLAlchemy async y la función `get_db_session` para inyección de dependencias
- [x] 3.3 Crear `src/app/db/base.py` con la clase base declarativa de SQLAlchemy
- [x] 3.4 Crear `src/app/main.py` con la instancia `FastAPI`, registro de routers y configuración de `CORSMiddleware` con `allow_credentials=True`
- [x] 3.5 Crear `src/app/routers/health.py` con `GET /health` que verifique conectividad a Postgres y Redis
- [x] 3.6 Verificar que `ruff check .` y `ruff format --check .` pasan sin errores

## 4. Celery worker

- [x] 4.1 Crear `src/app/worker/celery_app.py` con Celery configurado con Redis como broker y backend
- [x] 4.2 Crear tarea `health_check` de prueba que retorne `{"status": "ok"}`
- [x] 4.3 Crear `src/app/worker/tasks/__init__.py` con la tarea registrada

## 5. Modelo User y Alembic

- [x] 5.1 Crear `src/app/models/user.py` con modelo `User` (id UUID, email, hashed_password, is_active, created_at, updated_at)
- [x] 5.2 Inicializar Alembic: `alembic init alembic` y configurar `alembic.ini` para leer `DATABASE_URL` desde entorno
- [x] 5.3 Configurar `alembic/env.py` para usar el engine async y cargar los modelos de `src/app/db/base.py`
- [x] 5.4 Generar migración inicial: `alembic revision --autogenerate -m "create users table"`
- [x] 5.5 Verificar que la migración genera correctamente la tabla `users` con índice único en `email`

## 6. Autenticación JWT

- [x] 6.1 Crear `src/app/core/security.py` con funciones: `hash_password`, `verify_password`, `create_access_token`, `create_refresh_token`, `decode_token`
- [x] 6.2 Crear `src/app/schemas/auth.py` con schemas Pydantic: `RegisterRequest`, `LoginRequest`, `TokenResponse`, `UserResponse`
- [x] 6.3 Crear `src/app/services/auth_service.py` con lógica: registro, login, refresh (con rotación), logout
- [x] 6.4 Implementar almacenamiento de refresh tokens en Redis con TTL (para soporte de rotación e invalidación)
- [x] 6.5 Crear `src/app/routers/auth.py` con endpoints: `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`
- [x] 6.6 Crear dependencia `get_current_user` en `src/app/core/deps.py` que valide el access token JWT
- [x] 6.7 Registrar el router de auth en `main.py`

## 7. Tests del backend

- [x] 7.1 Crear `tests/conftest.py` con fixtures: base de datos de test (SQLite en memoria o Postgres de test), cliente HTTP async (`AsyncClient`), usuario de prueba
- [x] 7.2 Escribir tests para `GET /health`: respuesta 200 con todos los servicios disponibles
- [x] 7.3 Escribir tests para `POST /auth/register`: registro exitoso, email duplicado (409), contraseña débil (422)
- [x] 7.4 Escribir tests para `POST /auth/login`: login exitoso con cookie, credenciales inválidas (401)
- [x] 7.5 Escribir tests para `POST /auth/refresh`: refresh exitoso con rotación, token expirado (401), sin cookie (401)
- [x] 7.6 Escribir tests para `POST /auth/logout`: cookie limpiada correctamente
- [x] 7.7 Verificar que `pytest` pasa con cobertura > 80% en los módulos de auth

## 8. Scaffold del frontend

- [x] 8.1 Inicializar Next.js 15 en `/frontend` con TypeScript, App Router y Tailwind CSS: `npx create-next-app@latest frontend --typescript --tailwind --app --src-dir`
- [x] 8.2 Verificar que `tsconfig.json` tiene `"strict": true`
- [x] 8.3 Instalar dependencias adicionales: `zustand`, `react-hook-form`, `zod`, `@hookform/resolvers`
- [x] 8.4 Verificar versión compatible de shadcn/ui con Tailwind 4; inicializar con `npx shadcn@latest init`
- [x] 8.5 Instalar componente Button de shadcn: `npx shadcn@latest add button`
- [x] 8.6 Crear `/frontend/.env.example` con `NEXT_PUBLIC_API_URL=http://localhost:8000`
- [x] 8.7 Configurar ESLint con reglas de Next.js y TypeScript

## 9. Aplicación Next.js base

- [x] 9.1 Crear `src/lib/api-client.ts` con cliente HTTP que use `NEXT_PUBLIC_API_URL` como base URL
- [x] 9.2 Crear `src/store/index.ts` con un store Zustand base (con devtools en desarrollo)
- [x] 9.3 Actualizar `src/app/layout.tsx` con metadatos base (title: "Multifolio", description) y estilos globales de Tailwind
- [x] 9.4 Crear `src/app/page.tsx` con una página raíz básica que muestre el nombre del proyecto
- [x] 9.5 Verificar que `npm run build` pasa sin errores
- [x] 9.6 Verificar que `npm run lint` y `tsc --noEmit` pasan sin errores

## 10. Docker Compose

- [x] 10.1 Crear `Dockerfile` del backend: imagen Python 3.12-slim, instalar UV, copiar y sincronizar dependencias, entrypoint con migración Alembic + uvicorn
- [x] 10.2 Crear `Dockerfile` del frontend: imagen Node LTS, instalar dependencias, build Next.js, `next start`
- [x] 10.3 Crear `docker-compose.yml` con los 5 servicios: `api`, `frontend`, `postgres`, `redis`, `worker`; healthchecks en `postgres` y `redis`; dependencias con `condition: service_healthy`
- [x] 10.4 Configurar volúmenes de código fuente para hot reload en `api` y `frontend`
- [x] 10.5 Publicar puertos: `api:8000`, `frontend:3000`, `postgres:5432`, `redis:6379`
- [x] 10.6 Verificar que `docker compose up` levanta los 5 servicios sin errores
- [x] 10.7 Verificar que `GET http://localhost:8000/health` retorna 200 con el stack corriendo
- [x] 10.8 Verificar que `http://localhost:3000` carga la página raíz correctamente

## 11. GitHub Actions CI

- [x] 11.1 Crear `.github/workflows/backend.yml` con path filter `backend/**`, jobs: `lint` (ruff), `test` (pytest con servicios postgres y redis), caché de UV
- [x] 11.2 Crear `.github/workflows/frontend.yml` con path filter `frontend/**`, jobs: `lint` (eslint), `type-check` (tsc), `build` (next build), caché de npm
- [x] 11.3 Abrir PR a `main` y verificar que ambos workflows corren en verde
