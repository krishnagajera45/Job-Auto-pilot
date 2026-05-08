from __future__ import annotations

import uuid
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Job Autopilot Notifications Service", version="0.1.0")


class NotificationRequest(BaseModel):
    user_id: str
    channel: str
    message: str


class PreferencesRequest(BaseModel):
    user_id: str
    email: bool = True
    sms: bool = False
    in_app: bool = True


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "service": "notifications-service"}


@app.post("/v1/notifications/send")
async def send_notification(request: NotificationRequest) -> dict:
    notification_id = str(uuid.uuid4())
    return {"notification_id": notification_id, "status": "sent", "channel": request.channel}


@app.post("/v1/notifications/preferences")
async def update_preferences(request: PreferencesRequest) -> dict:
    return {"status": "updated", "preferences": request.model_dump()}
