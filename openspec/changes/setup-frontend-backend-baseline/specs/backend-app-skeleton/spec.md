## ADDED Requirements

### Requirement: Estructura de módulos FastAPI
La aplicación backend SHALL organizarse en módulos separados por responsabilidad dentro de `src/app/`: `routers/`, `models/`, `schemas/`, `services/`, `core/`, `db/`. El archivo de entrada SHALL ser `src/app/main.py`.

#### Scenario: Aplicación importable sin errores
- **WHEN** se ejecuta `python -c "from app.main import app"` en `/backend`
- **THEN** la importación ocurre sin errores ni warnings

#### Scenario: Estructura de directorios correcta
- **WHEN** el desarrollador inspecciona `/backend/src/app/`
- **THEN** existen los subdirectorios: `routers/`, `models/`, `schemas/`, `services/`, `core/`, `db/`

### Requirement: Endpoint de health check
El servidor SHALL exponer `GET /health` que retorna el estado de la aplicación sin requerir autenticación. Este endpoint SHALL verificar conectividad con la base de datos y Redis.

#### Scenario: Health check exitoso
- **WHEN** se realiza `GET /health` con todos los servicios disponibles
- **THEN** la respuesta es HTTP 200
- **THEN** el body contiene `{"status": "ok", "database": "ok", "redis": "ok"}`

#### Scenario: Health check con dependencia caída
- **WHEN** se realiza `GET /health` con la base de datos no disponible
- **THEN** la respuesta es HTTP 503
- **THEN** el body contiene el componente fallido con su estado

### Requirement: Configuración mediante Pydantic Settings
Toda la configuración de la aplicación SHALL cargarse mediante una clase `Settings` que extiende `pydantic_settings.BaseSettings`. Los valores SHALL leerse desde variables de entorno. El acceso a configuración SHALL hacerse mediante un singleton compartido.

#### Scenario: Configuración cargada desde entorno
- **WHEN** las variables de entorno están presentes
- **THEN** `Settings()` instancia correctamente sin errores de validación

#### Scenario: Error explícito por variable faltante
- **WHEN** falta una variable de entorno obligatoria (ej. `DATABASE_URL`)
- **THEN** la aplicación falla al arrancar con un mensaje claro indicando qué variable falta

### Requirement: Sesión de base de datos async
El backend SHALL usar SQLAlchemy 2.0 en modo async con `asyncpg` como driver. Las sesiones de base de datos SHALL inyectarse mediante FastAPI `Depends`. No SHALL existir ninguna operación de base de datos síncrona.

#### Scenario: Sesión inyectada correctamente en router
- **WHEN** un endpoint utiliza `Depends(get_db_session)`
- **THEN** recibe una `AsyncSession` válida
- **THEN** la sesión se cierra automáticamente al finalizar el request

### Requirement: Celery worker configurado
El módulo `src/app/worker/celery_app.py` SHALL configurar Celery con Redis como broker y backend de resultados. La cola `default` SHALL ser la única cola activa en esta fase.

#### Scenario: Worker conecta con Redis
- **WHEN** se inicia el contenedor `worker`
- **THEN** Celery conecta con Redis sin errores
- **THEN** el worker queda en estado `ready` esperando tareas

#### Scenario: Tarea de prueba ejecutable
- **WHEN** se encola la tarea `health_check` desde el API
- **THEN** el worker la procesa y retorna resultado en menos de 5 segundos
