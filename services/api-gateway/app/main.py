from __future__ import annotations

import logging
import os
from typing import Dict, Literal, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI(title="Job Autopilot API Gateway", version="0.1.0")
logger = logging.getLogger(__name__)

SERVICE_URLS: Dict[str, str] = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
    "resume": os.getenv("RESUME_SERVICE_URL", "http://resume-service:8002"),
    "job_ingestion": os.getenv("JOB_INGESTION_SERVICE_URL", "http://job-ingestion-service:8003"),
    "agent": os.getenv("AGENT_SERVICE_URL", "http://agent-orchestration-service:8004"),
    "rag": os.getenv("RAG_SERVICE_URL", "http://rag-memory-service:8005"),
    "automation": os.getenv("AUTOMATION_SERVICE_URL", "http://application-automation-service:8006"),
    "notifications": os.getenv("NOTIFICATIONS_SERVICE_URL", "http://notifications-service:8007"),
    "analytics": os.getenv("ANALYTICS_SERVICE_URL", "http://analytics-service:8008"),
    "messaging": os.getenv("MESSAGING_SERVICE_URL", "http://messaging-service:8010"),
}


class JobIntakeRequest(BaseModel):
    source: Literal["job_link", "job_id"] = Field(..., description="job_link or job_id")
    job_link: Optional[HttpUrl] = None
    job_id: Optional[str] = None
    user_id: Optional[str] = None


class ChannelIntakeRequest(BaseModel):
    user_id: str
    user_handle: str
    channel: Literal["telegram", "whatsapp"]
    message: str
    job_link: Optional[HttpUrl] = None
    job_description: Optional[str] = None
    name: str = "Candidate"
    job_title: str = "Role"
    company: str = "Company"
    template_name: str = "default"


class JobFetchRequest(BaseModel):
    job_link: HttpUrl
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
            logger.exception("Job ingestion service error")
            raise HTTPException(status_code=502, detail="Job ingestion service unavailable") from exc
    return response.json()


@app.post("/v1/jobs/fetch")
async def fetch_job(request: JobFetchRequest) -> dict:
    url = f"{SERVICE_URLS['job_ingestion']}/v1/jobs/fetch"
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.post(url, json=request.model_dump())
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("Job fetch service error")
            raise HTTPException(status_code=502, detail="Job fetch unavailable") from exc
    return response.json()


@app.post("/v1/channels/intake")
async def intake_channel(request: ChannelIntakeRequest) -> dict:
    url = f"{SERVICE_URLS['messaging']}/v1/channels/intake"
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            response = await client.post(url, json=request.model_dump())
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("Messaging service error")
            raise HTTPException(status_code=502, detail="Messaging service unavailable") from exc
    return response.json()
