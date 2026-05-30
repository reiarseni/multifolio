## ADDED Requirements

### Requirement: Monorepo directory structure
El repositorio SHALL contener dos workspaces en la raíz: `/backend` para el servidor FastAPI y `/frontend` para la aplicación Next.js. Ningún código de aplicación SHALL residir en la raíz del repo.

#### Scenario: Backend workspace inicializado
- **WHEN** el desarrollador clona el repositorio
- **THEN** existe `/backend/pyproject.toml` con UV como gestor de dependencias
- **THEN** existe `/backend/src/app/` como directorio raíz de módulos Python
- **THEN** `uv sync` dentro de `/backend` instala todas las dependencias sin errores

#### Scenario: Frontend workspace inicializado
- **WHEN** el desarrollador clona el repositorio
- **THEN** existe `/frontend/package.json` con Next.js 15 como dependencia
- **THEN** existe `/frontend/src/app/` como directorio raíz del App Router
- **THEN** `npm install` dentro de `/frontend` instala todas las dependencias sin errores

### Requirement: Linting y formateo backend
El backend SHALL configurar Ruff para linting y formateo. La configuración SHALL vivir en `pyproject.toml`. `ruff check .` y `ruff format --check .` DEBEN pasar sin errores en el scaffold inicial.

#### Scenario: Ruff configurado correctamente
- **WHEN** se ejecuta `ruff check .` en `/backend`
- **THEN** el comando termina con código de salida 0

#### Scenario: Formateo consistente
- **WHEN** se ejecuta `ruff format --check .` en `/backend`
- **THEN** el comando termina con código de salida 0

### Requirement: Linting y tipado frontend
El frontend SHALL configurar ESLint con las reglas de Next.js y TypeScript en modo estricto (`strict: true` en `tsconfig.json`). `npm run lint` DEBEN pasar sin errores en el scaffold inicial.

#### Scenario: ESLint pasa en scaffold inicial
- **WHEN** se ejecuta `npm run lint` en `/frontend`
- **THEN** el comando termina con código de salida 0

#### Scenario: TypeScript sin errores
- **WHEN** se ejecuta `npm run type-check` (o `tsc --noEmit`) en `/frontend`
- **THEN** el comando termina con código de salida 0

### Requirement: Archivos de entorno documentados
Cada workspace SHALL proveer un archivo `.env.example` con todas las variables de entorno requeridas, con valores de ejemplo seguros. El archivo `.env` real SHALL estar en `.gitignore`.

#### Scenario: Variables de entorno backend documentadas
- **WHEN** el desarrollador consulta `/backend/.env.example`
- **THEN** encuentra todas las variables necesarias: DATABASE_URL, REDIS_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, ALLOWED_ORIGINS

#### Scenario: Variables de entorno frontend documentadas
- **WHEN** el desarrollador consulta `/frontend/.env.example`
- **THEN** encuentra todas las variables necesarias: NEXT_PUBLIC_API_URL
