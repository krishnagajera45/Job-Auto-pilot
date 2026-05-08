# API Gateway Service

## Responsibilities
- Single entry point for the Job Autopilot platform.
- Routes job intake, document tailoring, and application requests to downstream services.
- Aggregates service health for dashboard readiness checks.

## Key Endpoints
- `GET /health`
- `GET /ready`
- `GET /v1/services`
- `POST /v1/jobs/intake`

## Configuration
Configure downstream services via environment variables:
- `AUTH_SERVICE_URL`
- `RESUME_SERVICE_URL`
- `JOB_INGESTION_SERVICE_URL`
- `AGENT_SERVICE_URL`
- `RAG_SERVICE_URL`
- `AUTOMATION_SERVICE_URL`
- `NOTIFICATIONS_SERVICE_URL`
- `ANALYTICS_SERVICE_URL`
