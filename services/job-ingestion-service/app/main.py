from __future__ import annotations

import uuid
from typing import Dict, Literal, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI(title="Job Autopilot Job Ingestion Service", version="0.1.0")

JOBS: Dict[str, dict] = {}


class JobIngestRequest(BaseModel):
    source: Literal["job_link", "job_id"] = Field(..., description="job_link or job_id")
    job_link: Optional[HttpUrl] = None
    job_id: Optional[str] = None
    user_id: Optional[str] = None


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "service": "job-ingestion-service"}


@app.post("/v1/jobs/ingest")
async def ingest_job(request: JobIngestRequest) -> dict:
    job_uuid = str(uuid.uuid4())
    JOBS[job_uuid] = {
        "id": job_uuid,
        "source": request.source,
        "job_link": str(request.job_link) if request.job_link else None,
        "job_id": request.job_id,
        "user_id": request.user_id,
        "status": "parsed",
        "requirements": ["python", "fastapi", "llm"],
    }
    return JOBS[job_uuid]


@app.get("/v1/jobs/{job_id}")
async def get_job(job_id: str) -> dict:
    return JOBS.get(job_id, {"id": job_id, "status": "unknown"})
