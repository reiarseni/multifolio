# Tasks for feat-25-social-login

## Task 1: Add httpx-oauth dependency
- [x] Add `httpx-oauth>=0.13.0` to `backend/pyproject.toml` dependencies
- [x] Run `cd backend && uv sync` to install

## Task 2: Add OAuth config fields
- [x] Add `google_client_id: str = ""` to `backend/src/app/core/config.py`
- [x] Add `google_client_secret: str = ""`
- [x] Add `github_client_id: str = ""`
- [x] Add `github_client_secret: str = ""`

## Task 3: Create OAuth client module
- [x] Create `backend/src/app/core/oauth.py`
- [x] Configure Google OAuth2 client using httpx-oauth
- [x] Configure GitHub OAuth2 client using httpx-oauth
- [x] Add state generation and validation helpers

## Task 4: Extend User model
- [x] Add `auth_provider: Mapped[str | None]` to `backend/src/app/models/user.py`
- [x] Add `provider_user_id: Mapped[str | None]`

## Task 5: Create Alembic migration
- [x] Generate migration for `auth_provider` and `provider_user_id` columns
- [x] Columns must be nullable (no impact on existing users)

## Task 6: Add social_login_or_register service
- [x] Add `social_login_or_register(db, provider, provider_user_id, email, name)` to `backend/src/app/services/auth_service.py`
- [x] Handle: email exists → link provider
- [x] Handle: email doesn't exist → create user with generated password

## Task 7: Add OAuth endpoints
- [x] Add `GET /auth/{provider}/login` endpoint to `backend/src/app/routers/auth.py`
- [x] Add `GET /auth/{provider}/callback` endpoint
- [x] Handle state validation, code exchange, user creation, token generation

## Task 8: Update frontend login page
- [x] Add "Continuar con Google" button to `frontend/src/app/login/page.tsx`
- [x] Add "Continuar con GitHub" button
- [x] Create `frontend/src/lib/api/auth.ts` with OAuth helpers

## Task 9: Update .env.example
- [x] Add `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- [x] Add `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`

## Task 10: Verify end-to-end
- [x] Run backend tests: `cd backend && uv run pytest`
- [x] Run frontend build: `cd frontend && npm run build`
- [x] Manual test: start services, click social login button, verify redirect
