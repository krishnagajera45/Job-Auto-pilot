# Architecture

## Microservices Overview
```mermaid
graph TD
  UI[Next.js Web UI] --> GW[API Gateway]
  GW --> AUTH[Auth/User Service]
  GW --> RESUME[Resume Service]
  GW --> JOBS[Job Ingestion Service]
  GW --> AGENT[Agent Orchestration Service]
  GW --> RAG[RAG/Memory Service]
  GW --> AUTO[Application Automation Service]
  GW --> NOTIFY[Notifications Service]
  GW --> ANALYTICS[Analytics Service]
  AGENT --> RAG
  AUTO --> NOTIFY
  RESUME --> STORAGE[(Object Storage)]
  AUTH --> DB[(Postgres/Supabase)]
  RAG --> VDB[(Qdrant/pgvector)]
```

## Tech Stack
- **APIs:** FastAPI
- **UI:** Next.js + Tailwind
- **Agent Orchestration:** LangGraph/LangChain, LangFlow
- **Tooling:** MCP/FastMCP
- **Memory:** Mem0
- **Model Serving:** vLLM / Ollama
- **Datastores:** Supabase/Postgres, Qdrant/pgvector, Redis
- **Queues:** RabbitMQ
- **Storage:** S3-compatible (MinIO)
- **Observability:** OpenTelemetry, Sentry, Prometheus-compatible metrics
- **Automation:** Playwright for ATS workflows
