from __future__ import annotations

import uuid
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Job Autopilot Application Automation Service", version="0.1.0")


class ApplicationRequest(BaseModel):
    user_id: str
    job_id: str
    resume_id: str
    cover_letter_id: Optional[str] = None
    approval_required: bool = True


class ApprovalRequest(BaseModel):
    approver_id: str
    decision: str


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "service": "application-automation-service"}


@app.post("/v1/applications/apply")
async def apply_to_job(request: ApplicationRequest) -> dict:
    application_id = str(uuid.uuid4())
    return {
        "application_id": application_id,
        "status": "pending-approval" if request.approval_required else "submitted",
        "job_id": request.job_id,
    }


@app.post("/v1/applications/{application_id}/approve")
async def approve_application(application_id: str, request: ApprovalRequest) -> dict:
    return {
        "application_id": application_id,
        "status": "submitted" if request.decision == "approve" else "rejected",
        "decision": request.decision,
    }


@app.get("/v1/applications/{application_id}")
async def get_application(application_id: str) -> dict:
    return {
        "application_id": application_id,
        "status": "tracking",
        "automation": "playwright",
    }
