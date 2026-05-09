from __future__ import annotations

import ipaddress
import re
import uuid
from html.parser import HTMLParser
from typing import Dict, Literal, Optional
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI(title="Job Autopilot Job Ingestion Service", version="0.1.0")

# Prototype-only in-memory storage; replace with persistent storage.
JOBS: Dict[str, dict] = {}

# Limit response size to keep downstream prompts bounded.
MAX_JOB_DESCRIPTION_LENGTH = 8000
ALLOWED_JOB_HOSTS = {
    "www.linkedin.com",
    "linkedin.com",
    "boards.greenhouse.io",
    "jobs.lever.co",
}
SAFE_PATH_PATTERN = re.compile(r"^/[A-Za-z0-9._~!$&'()*+,;=:@/\\-]*$")


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


def validate_job_link(job_link: str) -> str:
    parsed = urlparse(job_link)
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="Invalid job link scheme")
    hostname = parsed.hostname or ""
    if hostname not in ALLOWED_JOB_HOSTS:
        raise HTTPException(status_code=400, detail="Job link host is not supported")
    if re.fullmatch(r"[0-9a-fA-F:.]+", hostname):
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise HTTPException(status_code=400, detail="Private job links are not allowed")
    if hostname.endswith(".local"):
        raise HTTPException(status_code=400, detail="Local job links are not allowed")
    if not SAFE_PATH_PATTERN.fullmatch(parsed.path or "/"):
        raise HTTPException(status_code=400, detail="Job link path is invalid")
    return f"https://{hostname}{parsed.path}"


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

    safe_link = validate_job_link(str(request.job_link))
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            response = await client.get(safe_link)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="Unable to fetch job posting") from exc

    html = response.text
    title_match = re.search(r"(?is)<title>(.*?)</title>", html)
    description = extract_text(html)[:MAX_JOB_DESCRIPTION_LENGTH]
    return {
        "job_link": str(request.job_link),
        "title": title_match.group(1).strip() if title_match else "Job Posting",
        "description": description,
        "status": "fetched",
    }


@app.get("/v1/jobs/{job_id}")
async def get_job(job_id: str) -> dict:
    return JOBS.get(job_id, {"id": job_id, "status": "unknown"})
