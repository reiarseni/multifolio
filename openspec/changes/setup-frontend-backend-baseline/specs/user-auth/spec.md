## ADDED Requirements

### Requirement: Modelo User en base de datos
SHALL existir una tabla `users` con los campos: `id` (UUID), `email` (único, indexado), `hashed_password`, `is_active` (bool, default true), `created_at`, `updated_at`. El modelo SHALL usar SQLAlchemy 2.0 declarativo async.

#### Scenario: Tabla creada por migración Alembic
- **WHEN** se ejecuta `alembic upgrade head` en una base de datos vacía
- **THEN** existe la tabla `users` con todos los campos requeridos
- **THEN** existe un índice único en la columna `email`

### Requirement: Registro de usuario
`POST /auth/register` SHALL crear un nuevo usuario. La contraseña SHALL almacenarse como hash bcrypt. El email SHALL verificarse como único antes de crear el registro.

#### Scenario: Registro exitoso
- **WHEN** se realiza `POST /auth/register` con `{"email": "user@example.com", "password": "SecurePass123!"}`
- **THEN** la respuesta es HTTP 201
- **THEN** el body contiene `{"id": "<uuid>", "email": "user@example.com"}`
- **THEN** la contraseña en base de datos es un hash bcrypt, no el texto plano

#### Scenario: Email duplicado rechazado
- **WHEN** se realiza `POST /auth/register` con un email ya existente
- **THEN** la respuesta es HTTP 409
- **THEN** el body contiene `{"detail": "Email already registered"}`

#### Scenario: Contraseña débil rechazada
- **WHEN** se realiza `POST /auth/register` con contraseña de menos de 8 caracteres
- **THEN** la respuesta es HTTP 422

### Requirement: Login con emisión de tokens
`POST /auth/login` SHALL autenticar al usuario y emitir un access token JWT (body JSON) y un refresh token (httpOnly cookie).

#### Scenario: Login exitoso
- **WHEN** se realiza `POST /auth/login` con credenciales válidas
- **THEN** la respuesta es HTTP 200
- **THEN** el body contiene `{"access_token": "<jwt>", "token_type": "bearer"}`
- **THEN** la respuesta incluye un header `Set-Cookie` con `refresh_token` en atributos `HttpOnly; SameSite=Lax; Path=/auth/refresh`

#### Scenario: Credenciales inválidas rechazadas
- **WHEN** se realiza `POST /auth/login` con email o contraseña incorrectos
- **THEN** la respuesta es HTTP 401
- **THEN** el body contiene `{"detail": "Invalid credentials"}`

### Requirement: Refresh de access token
`POST /auth/refresh` SHALL emitir un nuevo access token a partir de un refresh token válido en la cookie httpOnly. El refresh token original SHALL invalidarse (rotación de tokens).

#### Scenario: Refresh exitoso
- **WHEN** se realiza `POST /auth/refresh` con una cookie `refresh_token` válida
- **THEN** la respuesta es HTTP 200
- **THEN** el body contiene un nuevo `access_token`
- **THEN** la respuesta incluye una nueva cookie `refresh_token` (rotación)
- **THEN** el refresh token anterior ya no es válido para futuros refreshes

#### Scenario: Refresh con token expirado rechazado
- **WHEN** se realiza `POST /auth/refresh` con un refresh token expirado
- **THEN** la respuesta es HTTP 401

#### Scenario: Refresh sin cookie rechazado
- **WHEN** se realiza `POST /auth/refresh` sin cookie `refresh_token`
- **THEN** la respuesta es HTTP 401

### Requirement: Logout
`POST /auth/logout` SHALL invalidar el refresh token y limpiar la cookie httpOnly.

#### Scenario: Logout exitoso
- **WHEN** se realiza `POST /auth/logout` con una cookie `refresh_token` válida
- **THEN** la respuesta es HTTP 200
- **THEN** la respuesta incluye `Set-Cookie` con `refresh_token=; Max-Age=0` para limpiar la cookie
- **THEN** el refresh token ya no puede usarse para refresh posteriores

### Requirement: Dependencia de usuario autenticado
SHALL existir una dependencia FastAPI `get_current_user` que valide el access token JWT del header `Authorization: Bearer <token>` y retorne el usuario activo.

#### Scenario: Token válido resuelve usuario
- **WHEN** un endpoint protegido recibe un request con `Authorization: Bearer <valid_token>`
- **THEN** la dependencia retorna el objeto `User` correspondiente

#### Scenario: Token inválido rechazado
- **WHEN** un endpoint protegido recibe un token expirado o malformado
- **THEN** la respuesta es HTTP 401

#### Scenario: Usuario inactivo rechazado
- **WHEN** el token es válido pero `user.is_active` es false
- **THEN** la respuesta es HTTP 403

### Requirement: CORS configurado para httpOnly cookies
El middleware CORS SHALL configurarse con `allow_credentials=True` y los origins del frontend explícitamente listados. Wildcards SHALL estar prohibidos cuando `allow_credentials=True`.

#### Scenario: CORS permite requests con credenciales desde el frontend
- **WHEN** el frontend en `http://localhost:3000` realiza un request con `credentials: 'include'`
- **THEN** la respuesta incluye los headers CORS correctos
- **THEN** el browser no bloquea el request por política CORS
