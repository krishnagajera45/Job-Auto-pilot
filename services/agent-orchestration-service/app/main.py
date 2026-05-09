from __future__ import annotations

import json
import logging
import os
import uuid
from pathlib import Path
from typing import Any, List, Literal, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI(title="Job Autopilot Agent Orchestration Service", version="0.1.0")
logger = logging.getLogger(__name__)

DEFAULT_OPENCLAW_CONFIG = {
    "llm": {"provider": "ollama", "model": "qwen2.5:3b"},
    "agents": [
        {"name": "job_fetcher"},
        {"name": "requirements_extractor"},
        {"name": "memory_retriever"},
        {"name": "resume_tailor"},
        {"name": "cover_letter_writer"},
        {"name": "latex_renderer"},
        {"name": "notifier"},
    ],
}


def load_openclaw_config() -> dict[str, Any]:
    config_path = Path(os.getenv("OPENCLAW_CONFIG_PATH", "/app/configs/openclaw.json"))
    if config_path.exists():
        return json.loads(config_path.read_text())
    logger.warning("OpenClaw config not found at %s, using defaults", config_path)
    return DEFAULT_OPENCLAW_CONFIG


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


class OpenClawRequest(BaseModel):
    user_id: str
    channel: Literal["telegram", "whatsapp"] = Field(default="telegram", description="telegram or whatsapp")
    job_link: Optional[HttpUrl] = None
    job_description: Optional[str] = None
    name: str = "Candidate"
    job_title: str = "Role"
    company: str = "Company"
    template_name: str = "default"


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


@app.get("/v1/openclaw/config")
async def openclaw_config() -> dict:
    return load_openclaw_config()


@app.post("/v1/workflows/openclaw")
async def run_openclaw_workflow(request: OpenClawRequest) -> dict:
    workflow_id = str(uuid.uuid4())
    config = load_openclaw_config()
    agents = [agent.get("name") for agent in config.get("agents", [])]
    resume_content = (
        f"Tailored resume for {request.job_title} at {request.company}.\n\n"
        f"Key highlights mapped to job requirements:\n- {request.job_description or 'Job description pending'}"
    )
    cover_letter_content = (
        f"Dear Hiring Manager,\n\n"
        f"I am excited to apply for the {request.job_title} role at {request.company}. "
        f"This letter was tailored from the provided job details.\n\n"
        f"Regards,\n{request.name}"
    )
    return {
        "workflow_id": workflow_id,
        "status": "queued",
        "status_detail": "placeholder-content",
        "channel": request.channel,
        "agents": agents,
        "resume_content": resume_content,
        "cover_letter_content": cover_letter_content,
        "job_link": str(request.job_link) if request.job_link else None,
    }
