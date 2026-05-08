# Resume Service

## Responsibilities
- Resume ingestion and versioning.
- Cover letter storage and retrieval.
- Supports multiple sources (upload, LinkedIn import, paste).

## Key Endpoints
- `POST /v1/resumes`
- `GET /v1/resumes`
- `POST /v1/resumes/{resume_id}/versions`
- `POST /v1/cover-letters`

## Prototype Note
Current implementation stores resumes and cover letters in memory. Persist to Postgres + object storage.
