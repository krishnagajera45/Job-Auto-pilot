# Job Autopilot

Agentic AI platform for automating job applications: intake a job link, tailor resumes and cover letters, and apply with approvals.

## Highlights
- Microservices architecture with FastAPI and Next.js.
- Agent orchestration with LangGraph/LangChain + MCP tools.
- RAG memory with vector storage (Qdrant/pgvector).
- Playwright-based application automation with audit logs.

## Repository Layout
- `frontend/`: Next.js dashboard and user experience.
- `services/`: FastAPI microservices (gateway, auth, resume, ingestion, orchestration, RAG, automation, notifications, analytics).
- `docs/`: product scope, architecture, workflows, and runbooks.
- `deploy/`: Kubernetes notes.

## Quick Start
```bash
cp .env.example .env
npm install --prefix frontend
pip install -r services/requirements.txt
docker compose up --build
```

Frontend: http://localhost:3000 (run separately via `npm run dev` in `frontend/`).

## Documentation
- [Product Scope](docs/product-scope.md)
- [User Journeys](docs/user-journeys.md)
- [Architecture](docs/architecture.md)
- [Data Models](docs/data-models.md)
- [Workflows](docs/workflows.md)
- [Deployment](docs/deployment.md)
- [Security](docs/security.md)
- [Operations](docs/operations.md)
- [Runbooks](docs/runbooks.md)
- [Roadmap](docs/roadmap.md)
- [OpenAPI Spec](docs/openapi/job-autopilot.yaml)

## Legacy Prototype
The `backend/` directory contains the original monolithic FastAPI prototype. It remains for reference but the new work is in `services/`.
