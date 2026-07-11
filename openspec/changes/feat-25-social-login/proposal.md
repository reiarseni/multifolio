## Why

El sistema de autenticación actual solo soporta email/contraseña. Los usuarios prefieren usar sus cuentas existentes (Google, GitHub) para autenticarse sin crear nuevas contraseñas. Esto reduce la fricción de registro y mejora la experiencia de usuario.

## What Changes

- Se agregan campos `auth_provider` y `provider_user_id` (nullable) al modelo User para vincular cuentas OAuth
- Se crea módulo de configuración OAuth con clients para Google y GitHub
- Se agrega service `social_login_or_register()` que maneja creación y vinculación automática de cuentas
- Se agregan endpoints `/auth/{provider}/callback` para procesar callbacks OAuth
- Se agregan botones de login social en la página de login del frontend
- Se agregan variables de entorno para client IDs y secrets de OAuth

## Capabilities

### New Capabilities
- `social-auth`: Autenticación OAuth 2.0 con Google y GitHub, incluyendo creación automática de cuentas y vinculación con cuentas existentes por email

### Modified Capabilities
- `user-auth`: Se extiende el modelo User con campos de proveedor OAuth (requerimientos de registro/login existentes no cambian)

## Impact

- **Modelo**: User recibe 2 columnas nuevas nullable (sin migración destructiva)
- **Dependencia**: `httpx-oauth>=0.13.0` en pyproject.toml
- **Config**: 4 variables de entorno nuevas (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`)
- **API**: 2 endpoints nuevos (`/auth/google/callback`, `/auth/github/callback`)
- **Frontend**: Modificación de login page, nuevo módulo `auth.ts` en lib/api
