from __future__ import annotations

import re
import uuid
from html.parser import HTMLParser
from typing import Dict, Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI(title="Job Autopilot Job Ingestion Service", version="0.1.0")

# Prototype-only in-memory storage; replace with persistent storage.
JOBS: Dict[str, dict] = {}


class JobIngestRequest(BaseModel):
    source: Literal["job_link", "job_id"] = Field(..., description="job_link or job_id")
    job_link: Optional[HttpUrl] = None
    job_id: Optional[str] = None
    user_id: Optional[str] = None


class JobFetchRequest(BaseModel):
    job_link: HttpUrl
    user_id: Optional[str] = None


class HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self._chunks.append(data.strip())

    def text(self) -> str:
        return " ".join(self._chunks)


def extract_text(html: str) -> str:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html)
    parser = HTMLTextExtractor()
    parser.feed(cleaned)
    return parser.text()


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


@app.post("/v1/jobs/fetch")
async def fetch_job_description(request: JobFetchRequest) -> dict:
    import httpx

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.get(str(request.job_link))
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="Unable to fetch job posting") from exc

    html = response.text
    title_match = re.search(r"(?is)<title>(.*?)</title>", html)
    description = extract_text(html)[:8000]
    return {
        "job_link": str(request.job_link),
        "title": title_match.group(1).strip() if title_match else "Job Posting",
        "description": description,
        "status": "fetched",
    }


@app.get("/v1/jobs/{job_id}")
async def get_job(job_id: str) -> dict:
    return JOBS.get(job_id, {"id": job_id, "status": "unknown"})
