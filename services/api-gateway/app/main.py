from __future__ import annotations

import os
from typing import Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI(title="Job Autopilot API Gateway", version="0.1.0")

SERVICE_URLS: Dict[str, str] = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
    "resume": os.getenv("RESUME_SERVICE_URL", "http://resume-service:8002"),
    "job_ingestion": os.getenv("JOB_INGESTION_SERVICE_URL", "http://job-ingestion-service:8003"),
    "agent": os.getenv("AGENT_SERVICE_URL", "http://agent-orchestration-service:8004"),
    "rag": os.getenv("RAG_SERVICE_URL", "http://rag-memory-service:8005"),
    "automation": os.getenv("AUTOMATION_SERVICE_URL", "http://application-automation-service:8006"),
    "notifications": os.getenv("NOTIFICATIONS_SERVICE_URL", "http://notifications-service:8007"),
    "analytics": os.getenv("ANALYTICS_SERVICE_URL", "http://analytics-service:8008"),
}


class JobIntakeRequest(BaseModel):
    source: str = Field(..., description="job_link or job_id")
    job_link: Optional[HttpUrl] = None
    job_id: Optional[str] = None
    user_id: Optional[str] = None


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "service": "api-gateway"}


@app.get("/ready")
async def readiness_check() -> dict:
    return {"status": "ready", "services": SERVICE_URLS}


@app.get("/v1/services")
async def list_services() -> dict:
    return {"services": SERVICE_URLS}


@app.post("/v1/jobs/intake")
async def intake_job(request: JobIntakeRequest) -> dict:
    url = f"{SERVICE_URLS['job_ingestion']}/v1/jobs/ingest"
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.post(url, json=request.model_dump())
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"Job ingestion service error: {exc}") from exc
    return response.json()
