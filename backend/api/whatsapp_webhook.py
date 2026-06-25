"""
WhatsApp Webhook Handler - Receives and processes WhatsApp messages
Supports job source selection keywords in messages
"""

from fastapi import APIRouter, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from models.core import InputSource, JobSource
from agents.orchestrator import run_workflow
from core.logger import get_logger

logger = get_logger("job_autopilot.api.whatsapp")

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


class WhatsAppMessage(BaseModel):
    """WhatsApp incoming message model"""
    From: str
    Body: str
    MessageSid: Optional[str] = None


@router.post("/webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    WhatsApp webhook endpoint
    Receives messages from Twilio and triggers workflow
    """
    # Get form data from Twilio
    form_data = await request.form()
    from_phone = form_data.get("From", "")
    message_body = form_data.get("Body", "")
    message_sid = form_data.get("MessageSid", "")
    
    logger.info(
        "WhatsApp message received",
        extra={
            "from": from_phone,
            "message_preview": message_body[:50],
            "message_sid": message_sid
        }
    )
    
    # Extract user ID from phone (in production, would query user database)
    user_id = extract_user_id_from_phone(from_phone)
    
    # Determine input source based on message content
    input_source = InputSource.WHATSAPP
    
    # Parse message to extract intent and job source
    # Simple parsing: if it's a URL, treat as job link
    if message_body.startswith("http"):
        input_source = InputSource.JOB_LINK
    
    # Detect job source preference from message keywords
    job_source = detect_job_source_from_message(message_body)
    
    # Add workflow execution to background tasks
    background_tasks.add_task(
        process_whatsapp_message,
        message_body=message_body,
        user_id=user_id,
        input_source=input_source,
        job_source=job_source,
        phone=from_phone
    )
    
    # Return 200 OK to acknowledge receipt
    return {"status": "message received"}


async def process_whatsapp_message(
    message_body: str,
    user_id: str,
    input_source: InputSource,
    job_source: JobSource,
    phone: str
):
    """
    Process WhatsApp message in background
    """
    logger.info(
        "Processing WhatsApp message in background",
        extra={
            "user_id": user_id,
            "phone": phone,
            "input_source": input_source.value,
            "job_source": job_source.value
        }
    )
    
    try:
        # Run workflow with job source preference
        result = await run_workflow(
            query=message_body,
            user_id=user_id,
            input_source=input_source,
            job_source=job_source
        )
        
        if result.errors:
            logger.warning(
                "Workflow completed with errors",
                extra={
                    "user_id": user_id,
                    "errors": result.errors
                }
            )
        else:
            logger.info(
                "Workflow completed successfully",
                extra={
                    "user_id": user_id,
                    "has_pdf": result.resume_pdf_path is not None
                }
            )
    
    except Exception as e:
        logger.error(
            "Failed to process WhatsApp message",
            extra={
                "user_id": user_id,
                "error": str(e)
            },
            exc_info=True
        )


def extract_user_id_from_phone(phone: str) -> str:
    """
    Extract user ID from phone number
    In production, would query database to find user by phone
    """
    # Remove 'whatsapp:' prefix if present
    phone = phone.replace("whatsapp:", "")
    # Use phone as user_id for mock implementation
    return f"user_{phone}"


def detect_job_source_from_message(message: str) -> JobSource:
    """
    Detect job source preference from message content
    
    Keywords:
    - "openclaw": Use OpenClaw API only
    - "brave": Use Brave Search only
    - "all" / "all sources": Use both sources
    
    Default: Brave Search (most reliable for general searches)
    """
    message_lower = message.lower()
    
    if "openclaw" in message_lower:
        logger.debug("Job source detected: OpenClaw")
        return JobSource.OPENCLAW
    
    if "all sources" in message_lower or "all boards" in message_lower:
        logger.debug("Job source detected: Both")
        return JobSource.BOTH
    
    if "brave" in message_lower:
        logger.debug("Job source detected: Brave Search")
        return JobSource.BRAVE_SEARCH
    
    # Default to Brave Search
    return JobSource.BRAVE_SEARCH


@router.get("/webhook")
async def whatsapp_webhook_verify(request: Request):
    """
    WhatsApp webhook verification (GET request)
    Twilio sends verification token to confirm webhook
    """
    # In production, verify the token from Twilio
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    logger.debug(
        "WhatsApp webhook verification request received",
        extra={"token_prefix": token[:10] if token else "None"}
    )
    
    # In production, verify token against environment variable
    # For now, accept any token
    if challenge:
        return {"challenge": challenge}
    
    return {"status": "error"}
