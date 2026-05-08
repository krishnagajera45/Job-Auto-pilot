from __future__ import annotations

from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Job Autopilot Analytics Service", version="0.1.0")


class AnalyticsEvent(BaseModel):
    user_id: str
    event_name: str
    payload: dict


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "service": "analytics-service"}


@app.post("/v1/analytics/events")
async def ingest_event(event: AnalyticsEvent) -> dict:
    return {"status": "ingested", "received_at": datetime.utcnow().isoformat()}


@app.get("/v1/analytics/summary")
async def summary(user_id: str) -> dict:
    return {
        "user_id": user_id,
        "applications": 3,
        "interviews": 1,
        "offers": 0,
    }
