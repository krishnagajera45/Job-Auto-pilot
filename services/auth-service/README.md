# Auth Service

## Responsibilities
- User registration, login, and refresh tokens.
- Role-based access control (admin/user).
- MFA enrollment and verification (placeholder for TOTP provider).

## Key Endpoints
- `POST /v1/auth/register`
- `POST /v1/auth/login`
- `POST /v1/auth/refresh`
- `POST /v1/auth/mfa/setup`
- `POST /v1/auth/mfa/verify`
- `GET /v1/users/me`
- `GET /v1/admin/health`
