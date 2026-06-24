"""
Job Link Handler - Processes direct job link submissions
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, HttpUrl
from models.core import InputSource
from agents.orchestrator import run_workflow
from core.logger import get_logger

logger = get_logger("job_autopilot.api.job_link")

router = APIRouter(prefix="/api", tags=["job-link"])


class JobLinkRequest(BaseModel):
    """Request to submit a job link"""
    job_link: HttpUrl
    user_id: str


class JobLinkResponse(BaseModel):
    """Response for job link submission"""
    status: str
    message: str
    job_link: str


@router.post("/job-link", response_model=JobLinkResponse)
async def submit_job_link(
    request: JobLinkRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit a job link directly for resume generation
    
    Args:
        request: JobLinkRequest with job link and user ID
    
    Returns:
        JobLinkResponse confirming submission
    """
    job_link = str(request.job_link)
    user_id = request.user_id
    
    logger.info(
        "Job link submitted",
        extra={
            "job_link": job_link,
            "user_id": user_id
        }
    )
    
    # Validate URL
    if not _is_valid_job_url(job_link):
        logger.warning(
            "Invalid job URL",
            extra={"job_link": job_link}
        )
        raise HTTPException(
            status_code=400,
            detail="Invalid job link. Must be from supported job boards (LinkedIn, Indeed, etc.)"
        )
    
    # Add workflow execution to background tasks
    background_tasks.add_task(
        process_job_link,
        job_link=job_link,
        user_id=user_id
    )
    
    logger.debug("Job link processing queued", extra={"user_id": user_id})
    
    return JobLinkResponse(
        status="queued",
        message="Job link received. Resume generation in progress.",
        job_link=job_link
    )


async def process_job_link(job_link: str, user_id: str):
    """
    Process job link in background
    """
    logger.info(
        "Processing job link in background",
        extra={
            "user_id": user_id,
            "job_link": job_link
        }
    )
    
    try:
        # Run workflow with job link as query
        result = await run_workflow(
            query=job_link,
            user_id=user_id,
            input_source=InputSource.JOB_LINK
        )
        
        if result.errors:
            logger.warning(
                "Job link processing completed with errors",
                extra={
                    "user_id": user_id,
                    "errors": result.errors
                }
            )
        else:
            logger.info(
                "Job link processing completed successfully",
                extra={
                    "user_id": user_id,
                    "has_pdf": result.resume_pdf_path is not None
                }
            )
    
    except Exception as e:
        logger.error(
            "Failed to process job link",
            extra={
                "user_id": user_id,
                "job_link": job_link,
                "error": str(e)
            },
            exc_info=True
        )


def _is_valid_job_url(url: str) -> bool:
    """
    Validate if URL is from a supported job board
    """
    supported_domains = [
        "linkedin.com",
        "indeed.com",
        "glassdoor.com",
        "dice.com",
        "monster.com",
        "ziprecruiter.com",
        "builtin.com",
        "stackoverflow.com",
    ]
    
    url_lower = url.lower()
    for domain in supported_domains:
        if domain in url_lower:
            return True
    
    return False


@router.get("/job-link/status/{request_id}")
async def get_job_link_status(request_id: str):
    """
    Get status of a job link processing request
    (Future feature: implement with database)
    """
    logger.debug("Status check requested", extra={"request_id": request_id})
    
    # TODO: Implement with database tracking
    return {
        "status": "processing",
        "message": "Your resume is being generated. You'll receive a WhatsApp message when ready."
    }
