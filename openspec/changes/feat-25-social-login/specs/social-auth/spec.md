## ADDED Requirements

### Requirement: OAuth login with Google
The system SHALL allow users to authenticate via OAuth 2.0 with Google. The frontend SHALL display a "Continuar con Google" button on the login page.

#### Scenario: Successful Google login
- **WHEN** user clicks "Continuar con Google" and completes the OAuth flow
- **THEN** system creates a session with JWT access token and httpOnly refresh token cookie

#### Scenario: First Google login creates account
- **WHEN** user authenticates with Google for the first time (email not in system)
- **THEN** system creates a new User with is_active=True, auth_provider="google", and provider_user_id set to Google's sub claim

#### Scenario: Google login links to existing account
- **WHEN** user authenticates with Google and email matches an existing User
- **THEN** system links the Google provider to the existing account (sets auth_provider and provider_user_id) and creates a session

### Requirement: OAuth login with GitHub
The system SHALL allow users to authenticate via OAuth 2.0 with GitHub. The frontend SHALL display a "Continuar con GitHub" button on the login page.

#### Scenario: Successful GitHub login
- **WHEN** user clicks "Continuar con GitHub" and completes the OAuth flow
- **THEN** system creates a session with JWT access token and httpOnly refresh token cookie

#### Scenario: First GitHub login creates account
- **WHEN** user authenticates with GitHub for the first time (email not in system)
- **THEN** system creates a new User with is_active=True, auth_provider="github", and provider_user_id set to GitHub's user ID

#### Scenario: GitHub login links to existing account
- **WHEN** user authenticates with GitHub and email matches an existing User
- **THEN** system links the GitHub provider to the existing account and creates a session

### Requirement: OAuth state parameter for CSRF protection
The system SHALL generate and validate a state parameter in the OAuth authorization request to prevent CSRF attacks.

#### Scenario: Invalid state parameter rejected
- **WHEN** callback receives an invalid or missing state parameter
- **THEN** system returns 403 Forbidden and does not create a session

### Requirement: User model stores OAuth provider data
The User model SHALL include fields for auth_provider (nullable String) and provider_user_id (nullable String).

#### Scenario: User created via email/password has null provider fields
- **WHEN** user registers via email/password
- **THEN** auth_provider and provider_user_id are NULL

### Requirement: Refresh token stored in Redis for social login
The system SHALL store the refresh token in Redis for social login users, identical to the email/password flow.

#### Scenario: Social login refresh token rotation
- **WHEN** a social login user refreshes their token
- **THEN** system rotates the refresh token in Redis following the same rotation logic as email/password login
