# Services Overview

Each service is a FastAPI application packaged with its own Dockerfile. Build them via Docker Compose from the repository root.

| Service | Port | Description |
| --- | --- | --- |
| api-gateway | 8000 | Entry point and routing layer |
| auth-service | 8001 | Authentication, RBAC, MFA |
| resume-service | 8002 | Resume and cover letter management |
| job-ingestion-service | 8003 | Job parsing and normalization |
| agent-orchestration-service | 8004 | LangGraph workflow orchestration |
| rag-memory-service | 8005 | Memory and retrieval service |
| application-automation-service | 8006 | ATS automation + approvals |
| notifications-service | 8007 | Email/SMS/in-app notifications |
| analytics-service | 8008 | Analytics event ingestion |
| messaging-service | 8010 | Telegram/WhatsApp intake |

OpenClaw configuration lives in `services/configs/openclaw.json` and is loaded by the agent orchestration service.
