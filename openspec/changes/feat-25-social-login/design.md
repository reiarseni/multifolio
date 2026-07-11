## Overview

Add OAuth 2.0 login with Google and GitHub to the existing JWT authentication system. The approach uses `httpx-oauth` (async-native, lightweight) as the OAuth client library. Social login creates or links accounts automatically based on email matching.

## Architecture Decisions

### Decision: Use httpx-oauth over authlib
- **Choice**: `httpx-oauth>=0.13.0`
- **Why**: Async-native, lighter dependency tree, maintained by tiangolo (FastAPI ecosystem), simpler API for OAuth2
- **Tradeoff**: Less flexible for complex OAuth flows, but sufficient for standard social login

### Decision: Nullable provider fields on User model
- **Choice**: Add `auth_provider` and `provider_user_id` as nullable columns
- **Why**: Backward compatible — existing email/password users unaffected. No need for separate OAuthAccount table for 2 providers
- **Tradeoff**: If many providers added later, a separate table would be cleaner (but that's out of scope)

### Decision: State parameter stored in session/cookie
- **Choice**: Generate random state, store in a short-lived cookie, validate on callback
- **Why**: Simple CSRF protection without additional state storage (Redis not needed for state)
- **Tradeoff**: Cookie size limit, but only one state at a time

### Decision: Frontend initiates OAuth redirect
- **Choice**: Frontend calls `GET /auth/{provider}/login` which returns the authorization URL, then redirects the browser
- **Why**: Clean separation — backend generates URL, frontend handles redirect. Works with Next.js App Router

## Components

### Backend Changes

**New file: `backend/src/app/core/oauth.py`**
- Configure `httpx-oauth` clients for Google and GitHub
- Functions: `get_google_client()`, `get_github_client()`
- State generation and validation helpers

**Modified: `backend/src/app/models/user.py`**
- Add `auth_provider: Mapped[str | None]` (String nullable)
- Add `provider_user_id: Mapped[str | None]` (String nullable)

**Modified: `backend/src/app/services/auth_service.py`**
- New function: `social_login_or_register(db, provider, provider_user_id, email, name) -> User`
  - Look up user by email
  - If exists: link provider (set auth_provider, provider_user_id) if not already linked
  - If not exists: create new User with auth_provider, provider_user_id, generated password hash
  - Return User

**Modified: `backend/src/app/routers/auth.py`**
- New endpoint: `GET /auth/{provider}/login` — returns authorization URL with state
- New endpoint: `GET /auth/{provider}/callback` — handles OAuth callback, creates user/session, returns tokens

**Modified: `backend/src/app/core/config.py`**
- Add: `google_client_id`, `google_client_secret`, `github_client_id`, `github_client_secret`

**New migration: `backend/alembic/versions/xxx_add_social_auth_fields.py`**
- Add `auth_provider` and `provider_user_id` columns to users table (nullable)

**Modified: `backend/pyproject.toml`**
- Add dependency: `httpx-oauth>=0.13.0`

### Frontend Changes

**Modified: `frontend/src/app/login/page.tsx`**
- Add "Continuar con Google" button
- Add "Continuar con GitHub" button
- Both call `/auth/{provider}/login` and redirect

**New file: `frontend/src/lib/api/auth.ts`**
- `getOAuthUrl(provider)` — calls backend to get authorization URL
- Handles redirect flow

**Modified: `.env.example`**
- Add `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`

## Data Model

```
User (existing fields + new)
├── id: UUID (PK)
├── email: String(255) UNIQUE NOT NULL
├── hashed_password: String(255) NOT NULL  ← generated for social users too
├── is_active: Boolean DEFAULT True
├── auth_provider: String NULL             ← NEW
├── provider_user_id: String NULL          ← NEW
├── created_at: DateTime
└── updated_at: DateTime
```

## OAuth Flow

```
Frontend                    Backend                     Provider
   │                           │                           │
   ├── GET /auth/google/login ─┤                           │
   │                           ├── Generate state          │
   │                           ├── Store state in cookie   │
   │                           ├── Return auth URL         │
   │   ◄── redirect ──────────┤                           │
   │ ────────────────────────────────────────────────────► │
   │                           │   ◄── callback + code ── │
   │                           ├── Validate state          │
   │                           ├── Exchange code for token │
   │   │                       │   ──────────────────────►│
   │   │                       │   ◄── user info ─────────│
   │                           ├── social_login_or_register│
   │                           ├── Create JWT tokens      │
   │                           ├── Store refresh in Redis │
   │   ◄── set cookie + tokens┤                           │
   │   ├── Redirect to /dashboard                         │
```

## Security Considerations

- State parameter prevents CSRF on OAuth callback
- Refresh token stored in Redis with TTL (same as email/password flow)
- `hashed_password` is generated for social users (random bcrypt hash) — they can't login with password but the field stays NOT NULL
- Timing-attack protection not needed for social login (no password comparison)
- `secure` cookie flag controlled by `settings.is_production`
