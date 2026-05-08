# Job Ingestion Service

## Responsibilities
- Accept job links or IDs.
- Parse job descriptions, requirements, and metadata.
- Normalize results for downstream workflows.

## Key Endpoints
- `POST /v1/jobs/ingest`
- `GET /v1/jobs/{job_id}`

## Prototype Note
Current implementation stores parsed jobs in memory. Persist to Postgres and object storage for long-term tracking.
