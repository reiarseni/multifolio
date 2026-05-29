## Context

Multifolio es un proyecto greenfield. No existe ningún código de aplicación. El stack tecnológico está completamente definido en la especificación de producto: FastAPI (backend), Next.js 15 App Router (frontend), PostgreSQL 16, Redis 7, Celery, Docker Compose y GitHub Actions CI.

Esta es la primera y más crítica inversión de infraestructura: las decisiones tomadas aquí moldean el desarrollo de cada feature posterior.

## Goals / Non-Goals

**Goals:**
- Monorepo funcional con `/backend` y `/frontend` como workspaces independientes
- Stack verificado end-to-end: un request desde el browser llega al API y a la base de datos
- Autenticación JWT completa con refresh tokens seguros (httpOnly cookie) como base de todas las features que requieran identidad
- Entorno de desarrollo reproducible en un solo comando (`docker compose up`)
- CI verde desde el primer commit

**Non-Goals:**
- UI de autenticación (páginas de login/registro) — es feature, no infraestructura
- Features de dominio (perfil, facetas, PDF)
- Optimizaciones de rendimiento o configuración de producción
- Sistema de emails transaccionales

## Decisions

### D1 — Estructura de directorios del backend

**Decisión**: `src/app/` como raíz de módulos con subdirectorios por capa: `routers/`, `models/`, `schemas/`, `services/`, `core/`, `db/`, `worker/`.

**Alternativa considerada**: estructura plana (`app/routers.py`, `app/models.py`). Rechazada porque no escala cuando cada entidad del dominio (User, Profile, Facet, Project) tiene su propio conjunto de archivos.

**Rationale**: FastAPI no impone estructura; esta convención de módulos por capa está ampliamente adoptada y permite localizar cualquier artefacto por tipo sin conocer el dominio.

---

### D2 — Almacenamiento del refresh token

**Decisión**: El refresh token vive en una cookie httpOnly con atributos `SameSite=Lax; Path=/auth/refresh; Secure` (Secure solo en producción). El access token se retorna en el body JSON y vive en memoria del cliente (no en localStorage).

**Alternativa considerada**: ambos tokens en localStorage. Rechazada — localStorage es accesible desde JavaScript y cualquier librería de terceros comprometida puede exfiltrar los tokens (XSS).

**Alternativa considerada**: ambos tokens en httpOnly cookie. Rechazada — el access token en cookie requiere configuración CSRF adicional; en memoria es más simple y la ventana de exposición es mínima (tiempo de vida corto).

**Rationale**: La combinación access-en-memoria + refresh-en-httpOnly es el patrón recomendado por OWASP para SPAs. El CORS con `allow_credentials=True` y origins explícitos compensa la restricción de `SameSite=Lax` cross-origin en desarrollo.

**Implicación en Next.js 15**: `cookies()` es API async en el App Router. El middleware de auth del frontend debe usar `await cookies()` para leer el estado de sesión en Server Components.

---

### D3 — Rotación de refresh tokens

**Decisión**: En cada `POST /auth/refresh`, el token anterior se invalida y se emite uno nuevo (rotación). Los tokens usados se rastrean en Redis con TTL igual a su expiración.

**Alternativa considerada**: refresh tokens estáticos (un token válido hasta que expira). Rechazada porque si el token es robado, el atacante tiene acceso indefinido hasta la expiración.

**Rationale**: La rotación convierte el robo en detectable: si el token legítimo falla porque alguien ya lo rotó, el sistema puede revocar la sesión completa.

---

### D4 — Auto-migración en entrypoint del contenedor api

**Decisión**: El entrypoint del contenedor `api` ejecuta `alembic upgrade head` antes de `uvicorn`. Si la migración falla, el contenedor sale con código no-cero.

**Alternativa considerada**: migración manual (`docker exec api alembic upgrade head`). Rechazada por la experiencia de desarrollo acordada: un solo comando debe levantar el entorno completo y funcional.

**Rationale**: En desarrollo local es la opción correcta. La nota para producción es que en entornos con múltiples réplicas del API, la migración debe correr desde un job dedicado (no desde el pod de la aplicación) para evitar condiciones de carrera — pero eso está fuera del scope de esta baseline.

---

### D5 — Una cola Celery por ahora

**Decisión**: Cola `default` única. No se separa la cola de PDF en esta fase.

**Rationale**: El único worker actual es de verificación de conectividad. Introducir múltiples colas sin tasks reales es configuración prematura. La separación es trivial cuando llega el feature de generación de PDF.

---

### D6 — Path filtering en CI

**Decisión**: Dos workflows independientes (`backend.yml`, `frontend.yml`) con `paths` filter. El workflow de backend se activa con cambios en `backend/**`; el de frontend con cambios en `frontend/**`. Ambos se activan si cambia la raíz del repo (`.github/**`, `docker-compose.yml`).

**Rationale**: En un monorepo, ejecutar el CI completo en cada commit desperdicia minutos de CI. El path filtering hace el feedback loop más rápido y el uso de Actions más eficiente.

---

### D7 — UV como gestor de dependencias Python

**Decisión**: UV en lugar de pip/poetry para el backend.

**Rationale**: UV está explícitamente especificado. Es 10-100x más rápido que pip en resolución e instalación. `uv sync` con lockfile garantiza builds reproducibles. La imagen Docker del backend puede aprovechar el caché de layers al separar `pyproject.toml` de `src/`.

## Risks / Trade-offs

| Riesgo | Mitigación |
|---|---|
| `SameSite=Lax` bloquea cookies en requests cross-origin en algunos flujos | Configurar `SameSite=None; Secure` solo en producción con HTTPS. En desarrollo, frontend y backend en puertos distintos del mismo `localhost` evitan el problema. |
| Auto-migración puede causar condiciones de carrera en futuros deploys multi-réplica | Documentar que en producción la migración debe correr desde un job dedicado antes del despliegue. |
| Next.js 15 rompe compatibilidad con librerías de auth que usan `cookies()` síncrono | Implementar el cliente de auth nativo desde el inicio con `await cookies()`; no usar next-auth v4 ni librerías que no soporten Next.js 15. |
| shadcn/ui + Tailwind 4 — combinación reciente con posibles incompatibilidades | Verificar versiones compatibles de shadcn/ui con Tailwind 4 al inicializar. La CLI de shadcn detecta la versión de Tailwind. |

## Migration Plan

Este es un proyecto greenfield — no hay código preexistente que migrar. El plan de despliegue de esta baseline es:

1. Crear estructura de directorios y archivos de configuración
2. Implementar backend: modelos, configuración, health endpoint, auth endpoints
3. Crear migración Alembic inicial (`alembic revision --autogenerate -m "initial"`)
4. Implementar frontend: scaffold Next.js, configurar Tailwind/shadcn, cliente HTTP
5. Configurar Docker Compose y verificar que `docker compose up` levanta todo
6. Configurar GitHub Actions workflows
7. PR a `main` con CI verde

## Open Questions

- **Nombre del paquete Python**: ¿`multifolio` o `app`? Usar `app` es más genérico y convencional para backends FastAPI contenerizados; `multifolio` es más explícito. — *Propuesta*: `app` dentro del contenedor, `multifolio-backend` como nombre en `pyproject.toml`.
- **Package manager frontend**: La spec menciona npm. ¿Hay preferencia por pnpm (más rápido, mejor para monorepos)? — *Propuesta*: npm para mantenerse en lo especificado; trivial de cambiar después.
