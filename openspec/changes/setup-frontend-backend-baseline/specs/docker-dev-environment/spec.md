## ADDED Requirements

### Requirement: Docker Compose con 5 servicios
El archivo `docker-compose.yml` SHALL definir los servicios: `api`, `frontend`, `postgres`, `redis`, `worker`. Un único comando `docker compose up` SHALL levantar el entorno completo de desarrollo.

#### Scenario: Todos los servicios arrancan
- **WHEN** se ejecuta `docker compose up` en la raíz del repositorio
- **THEN** los 5 servicios arrancan sin errores y quedan en estado `running`

#### Scenario: Dependencias entre servicios respetadas
- **WHEN** se inicia el stack
- **THEN** `api` y `worker` no arrancan hasta que `postgres` y `redis` pasen sus healthchecks
- **THEN** `frontend` arranca independientemente de los servicios backend

### Requirement: Healthchecks configurados
Cada servicio de infraestructura SHALL tener un healthcheck que permita a los servicios dependientes esperar su disponibilidad real, no solo su inicio.

#### Scenario: Postgres healthcheck
- **WHEN** el contenedor `postgres` está en estado healthy
- **THEN** acepta conexiones en el puerto 5432

#### Scenario: Redis healthcheck
- **WHEN** el contenedor `redis` está en estado healthy
- **THEN** responde a `PING` correctamente

### Requirement: Hot reload en desarrollo
Los servicios `api` y `frontend` SHALL soportar hot reload en modo desarrollo mediante volúmenes montados. Los cambios en el código fuente local SHALL reflejarse sin reiniciar los contenedores.

#### Scenario: Hot reload backend
- **WHEN** el desarrollador modifica un archivo Python en `/backend/src/`
- **THEN** uvicorn detecta el cambio y recarga el servidor automáticamente
- **THEN** el nuevo código es efectivo en menos de 3 segundos

#### Scenario: Hot reload frontend
- **WHEN** el desarrollador modifica un archivo en `/frontend/src/`
- **THEN** Next.js Fast Refresh actualiza el navegador automáticamente

### Requirement: Puertos publicados en desarrollo
Los servicios SHALL exponer puertos locales para acceso directo del desarrollador sin necesitar tunelizar a través de otros contenedores.

#### Scenario: Puertos accesibles localmente
- **WHEN** el stack está corriendo
- **THEN** `api` es accesible en `http://localhost:8000`
- **THEN** `frontend` es accesible en `http://localhost:3000`
- **THEN** `postgres` es accesible en `localhost:5432` (para herramientas como DBeaver)
- **THEN** `redis` es accesible en `localhost:6379`

### Requirement: Auto-migración al arrancar api
El contenedor `api` SHALL ejecutar `alembic upgrade head` antes de iniciar uvicorn. Si la migración falla, el contenedor SHALL terminar con error.

#### Scenario: Migración exitosa al arrancar
- **WHEN** el contenedor `api` inicia por primera vez con una base de datos vacía
- **THEN** Alembic crea todas las tablas definidas en el modelo inicial
- **THEN** uvicorn arranca después de la migración exitosa

#### Scenario: Error de migración detiene el servicio
- **WHEN** la migración de Alembic falla (ej. base de datos no disponible)
- **THEN** el contenedor `api` termina con código de salida no-cero
- **THEN** Docker Compose reporta el servicio como fallido
