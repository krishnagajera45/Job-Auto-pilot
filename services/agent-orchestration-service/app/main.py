from __future__ import annotations

import uuid
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Job Autopilot Agent Orchestration Service", version="0.1.0")


class TailorRequest(BaseModel):
    job_id: str
    resume_id: str
    user_id: str
    include_cover_letter: bool = True


class ApplyRequest(BaseModel):
    job_id: str
    resume_id: str
    user_id: str
    approval_required: bool = True


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "service": "agent-orchestration-service"}


@app.post("/v1/workflows/tailor")
async def run_tailor_workflow(request: TailorRequest) -> dict:
    workflow_id = str(uuid.uuid4())
    steps: List[str] = [
        "parse_job",
        "extract_requirements",
        "retrieve_memory",
        "tailor_resume",
        "tailor_cover_letter" if request.include_cover_letter else "skip_cover_letter",
        "quality_review",
    ]
    return {
        "workflow_id": workflow_id,
        "status": "queued",
        "steps": steps,
        "job_id": request.job_id,
    }


@app.post("/v1/workflows/apply")
async def run_apply_workflow(request: ApplyRequest) -> dict:
    workflow_id = str(uuid.uuid4())
    return {
        "workflow_id": workflow_id,
        "status": "pending-approval" if request.approval_required else "queued",
        "job_id": request.job_id,
        "resume_id": request.resume_id,
    }
