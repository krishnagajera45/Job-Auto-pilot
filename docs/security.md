# Security Model

## Authentication
- OAuth and email/password supported.
- JWT access + refresh tokens.
- Optional MFA with TOTP providers.

## Authorization
- Role-based access control (user/admin).
- Service-to-service auth via signed tokens.

## Secrets & Compliance
- Secrets loaded from environment variables or secret manager.
- Audit logs for approvals and submission actions.
- Consent tracking for automated applications.
