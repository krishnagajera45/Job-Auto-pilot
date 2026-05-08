# RAG & Memory Service

## Responsibilities
- Indexes user resumes, portfolios, and notes into vector storage.
- Serves retrieval-augmented queries for agent workflows.

## Key Endpoints
- `POST /v1/memory/index`
- `POST /v1/memory/query`
- `GET /v1/memory/sources`
