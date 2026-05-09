from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, Literal, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI(title="Job Autopilot Messaging Service", version="0.1.0")

SERVICE_URLS: Dict[str, str] = {
    "job_ingestion": os.getenv("JOB_INGESTION_SERVICE_URL", "http://job-ingestion-service:8003"),
    "agent": os.getenv("AGENT_SERVICE_URL", "http://agent-orchestration-service:8004"),
    "resume": os.getenv("RESUME_SERVICE_URL", "http://resume-service:8002"),
    "notifications": os.getenv("NOTIFICATIONS_SERVICE_URL", "http://notifications-service:8007"),
}


class ChannelIntakeRequest(BaseModel):
    user_id: str
    user_handle: str
    channel: Literal["telegram", "whatsapp"]
    message: str = Field(..., description="Raw message text from the channel")
    job_link: Optional[HttpUrl] = None
    job_description: Optional[str] = None
    name: str = "Candidate"
    job_title: str = "Role"
    company: str = "Company"
    template_name: str = "default"


class ChannelIntakeResponse(BaseModel):
    workflow_id: str
    status: str
    channel: str
    attachments: list[str]


def extract_job_link(message: str) -> Optional[str]:
    match = re.search(r"https?://\S+", message)
    return match.group(0) if match else None


@app.on_event("startup")
async def startup_event() -> None:
    app.state.http_client = httpx.AsyncClient(timeout=20)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await app.state.http_client.aclose()


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "service": "messaging-service"}


@app.post("/v1/channels/intake", response_model=ChannelIntakeResponse)
async def intake_channel_message(request: ChannelIntakeRequest) -> ChannelIntakeResponse:
    job_link = str(request.job_link) if request.job_link else extract_job_link(request.message)
    job_description = request.job_description

    client = app.state.http_client
    if job_link and not job_description:
        try:
            fetch_resp = await client.post(
                f"{SERVICE_URLS['job_ingestion']}/v1/jobs/fetch",
                json={"job_link": job_link, "user_id": request.user_id},
            )
            fetch_resp.raise_for_status()
            job_description = fetch_resp.json().get("description")
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail="Job fetch failed") from exc

    if not job_description:
        job_description = request.message

    try:
        openclaw_resp = await client.post(
            f"{SERVICE_URLS['agent']}/v1/workflows/openclaw",
            json={
                "user_id": request.user_id,
                "channel": request.channel,
                "job_link": job_link,
                "job_description": job_description,
                "name": request.name,
                "job_title": request.job_title,
                "company": request.company,
                "template_name": request.template_name,
            },
        )
        openclaw_resp.raise_for_status()
        openclaw_data = openclaw_resp.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="OpenClaw workflow failed") from exc

    try:
        render_resp = await client.post(
            f"{SERVICE_URLS['resume']}/v1/documents/render",
            json={
                "user_id": request.user_id,
                "job_id": openclaw_data.get("workflow_id"),
                "resume_content": openclaw_data.get("resume_content"),
                "cover_letter_content": openclaw_data.get("cover_letter_content"),
                "name": request.name,
                "job_title": request.job_title,
                "company": request.company,
                "template_name": request.template_name,
            },
        )
        render_resp.raise_for_status()
        render_data = render_resp.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Document rendering failed") from exc

    output_dir = Path(render_data.get("output_dir", "/tmp/job-autopilot/documents")).resolve()
    attachments = [
        render_data["resume"].get("pdf_path") or render_data["resume"].get("tex_path"),
        render_data["cover_letter"].get("pdf_path") or render_data["cover_letter"].get("tex_path"),
        render_data["resume"].get("docx_path"),
        render_data["cover_letter"].get("docx_path"),
    ]
    attachments = [
        item
        for item in attachments
        if item and output_dir in Path(item).resolve().parents
    ]

    try:
        notify_resp = await client.post(
            f"{SERVICE_URLS['notifications']}/v1/notifications/send-document",
            json={
                "user_id": request.user_id,
                "channel": request.channel,
                "message": "Your tailored resume and cover letter are ready.",
                "attachments": attachments,
            },
        )
        notify_resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Notification delivery failed") from exc

    return ChannelIntakeResponse(
        workflow_id=openclaw_data.get("workflow_id", "unknown"),
        status="delivered",
        channel=request.channel,
        attachments=attachments,
    )
