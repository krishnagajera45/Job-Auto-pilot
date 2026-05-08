from __future__ import annotations

import uuid
from typing import Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Job Autopilot Resume Service", version="0.1.0")

RESUMES: Dict[str, dict] = {}
COVER_LETTERS: Dict[str, dict] = {}


class ResumeCreateRequest(BaseModel):
    user_id: str
    title: str
    content: str
    source: Literal["upload", "linkedin", "paste"] = Field(
        default="upload",
        description="upload | linkedin | paste",
    )


class ResumeVersionRequest(BaseModel):
    content: str
    summary: Optional[str] = None


class CoverLetterRequest(BaseModel):
    user_id: str
    job_id: str
    content: str


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "service": "resume-service"}


@app.post("/v1/resumes")
async def create_resume(request: ResumeCreateRequest) -> dict:
    resume_id = str(uuid.uuid4())
    RESUMES[resume_id] = {
        "id": resume_id,
        "user_id": request.user_id,
        "title": request.title,
        "versions": [
            {
                "version_id": str(uuid.uuid4()),
                "content": request.content,
                "summary": "Initial version",
            }
        ],
    }
    return RESUMES[resume_id]


@app.get("/v1/resumes")
async def list_resumes(user_id: str) -> List[dict]:
    return [resume for resume in RESUMES.values() if resume["user_id"] == user_id]


@app.post("/v1/resumes/{resume_id}/versions")
async def add_version(resume_id: str, request: ResumeVersionRequest) -> dict:
    resume = RESUMES.get(resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    version = {
        "version_id": str(uuid.uuid4()),
        "content": request.content,
        "summary": request.summary or "Tailored version",
    }
    resume["versions"].append(version)
    return {"resume_id": resume_id, "version": version}


@app.post("/v1/cover-letters")
async def create_cover_letter(request: CoverLetterRequest) -> dict:
    cover_id = str(uuid.uuid4())
    COVER_LETTERS[cover_id] = {
        "id": cover_id,
        "user_id": request.user_id,
        "job_id": request.job_id,
        "content": request.content,
    }
    return COVER_LETTERS[cover_id]
