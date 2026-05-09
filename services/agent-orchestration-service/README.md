# Agent Orchestration Service

## Responsibilities
- Orchestrates LangGraph/LangChain workflows.
- Coordinates job parsing, RAG retrieval, tailoring, and approval gates.
- Loads OpenClaw agent definitions from `services/configs/openclaw.json`.

## Key Endpoints
- `POST /v1/workflows/tailor`
- `POST /v1/workflows/apply`
- `GET /v1/openclaw/config`
- `POST /v1/workflows/openclaw`
