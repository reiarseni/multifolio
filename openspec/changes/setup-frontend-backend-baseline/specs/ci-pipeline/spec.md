## ADDED Requirements

### Requirement: CI de backend en cada PR
SHALL existir un workflow de GitHub Actions para el backend que corra en cada pull request a `main`. El workflow SHALL incluir jobs de lint, type check y tests.

#### Scenario: Lint de backend pasa
- **WHEN** se abre o actualiza un PR
- **THEN** el job `backend-lint` ejecuta `ruff check .` y `ruff format --check .`
- **THEN** el job falla si hay algún error de lint o formato

#### Scenario: Tests de backend pasan
- **WHEN** se abre o actualiza un PR
- **THEN** el job `backend-test` levanta PostgreSQL y Redis como servicios
- **THEN** ejecuta `pytest` con cobertura de código
- **THEN** el job falla si algún test falla

### Requirement: CI de frontend en cada PR
SHALL existir un workflow de GitHub Actions para el frontend que corra en cada pull request a `main`. El workflow SHALL incluir jobs de lint, type check y build.

#### Scenario: Lint de frontend pasa
- **WHEN** se abre o actualiza un PR
- **THEN** el job `frontend-lint` ejecuta `npm run lint`
- **THEN** el job falla si hay errores de ESLint

#### Scenario: Type check de frontend pasa
- **WHEN** se abre o actualiza un PR
- **THEN** el job `frontend-type-check` ejecuta `tsc --noEmit`
- **THEN** el job falla si hay errores de TypeScript

#### Scenario: Build de frontend pasa
- **WHEN** se abre o actualiza un PR
- **THEN** el job `frontend-build` ejecuta `npm run build`
- **THEN** el job falla si el build de Next.js produce errores

### Requirement: Path filtering para eficiencia
Los workflows SHALL usar path filters para ejecutarse únicamente cuando los archivos relevantes del workspace cambian. El workflow de backend SHALL activarse solo si cambian archivos en `/backend/**`. El workflow de frontend SHALL activarse solo si cambian archivos en `/frontend/**`.

#### Scenario: Cambio solo en backend no dispara CI de frontend
- **WHEN** un PR modifica únicamente archivos en `/backend/`
- **THEN** el workflow de frontend no se ejecuta

#### Scenario: Cambio en ambos workspaces dispara ambos workflows
- **WHEN** un PR modifica archivos en `/backend/` y `/frontend/`
- **THEN** ambos workflows se ejecutan en paralelo

### Requirement: Caché de dependencias en CI
Los workflows SHALL cachear las dependencias de cada workspace para reducir tiempos de ejecución. Backend SHALL cachear el entorno UV. Frontend SHALL cachear `node_modules` vía la caché de npm/pnpm.

#### Scenario: Segunda ejecución más rápida por caché
- **WHEN** un PR actualiza código sin cambiar dependencias
- **THEN** el paso de instalación de dependencias usa la caché
- **THEN** el tiempo del job es significativamente menor que en la primera ejecución
