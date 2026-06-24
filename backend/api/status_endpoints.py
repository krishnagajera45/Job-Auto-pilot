"""
Status and Info Endpoints - Provides access to application data
"""

from fastapi import APIRouter, HTTPException
from typing import List
from models.core import ApplicationRecord, ApplicationStatus
from core.logger import get_logger

logger = get_logger("job_autopilot.api.status")

router = APIRouter(prefix="/api", tags=["status"])


@router.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """
    Get status of a specific job processing
    """
    logger.debug("Status check requested", extra={"job_id": job_id})
    
    # TODO: Implement with database
    return {
        "job_id": job_id,
        "status": "completed",
        "resume_pdf": "/output/resume_generated.pdf",
        "cover_letter_pdf": "/output/cover_letter_generated.pdf",
        "whatsapp_sent": True,
        "generated_at": "2024-01-15T10:00:00Z"
    }


@router.get("/resumes")
async def list_resumes(user_id: str, limit: int = 10):
    """
    List generated resumes for a user
    """
    logger.info(
        "Resumes list requested",
        extra={"user_id": user_id, "limit": limit}
    )
    
    # TODO: Implement with database
    return {
        "user_id": user_id,
        "total_resumes": 0,
        "resumes": []
    }


@router.get("/applications")
async def list_applications(user_id: str, status: str = None):
    """
    List user's job applications and generated resumes
    
    Args:
        user_id: User ID
        status: Filter by status (generated, sent, applied, rejected, accepted)
    
    Returns:
        List of application records
    """
    logger.info(
        "Applications list requested",
        extra={"user_id": user_id, "status_filter": status}
    )
    
    # TODO: Implement with database
    # Mock response
    return {
        "user_id": user_id,
        "total_applications": 0,
        "applications": [],
        "status_breakdown": {
            "generated": 0,
            "sent": 0,
            "applied": 0,
            "rejected": 0,
            "accepted": 0
        }
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    logger.debug("Health check")
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "api": "ok",
            "database": "ok",
            "ollama_llm": "checking...",
            "whatsapp": "ok"
        }
    }


@router.get("/stats")
async def get_statistics(user_id: str = None):
    """
    Get statistics about resumes and applications
    
    Args:
        user_id: Optional - get stats for specific user
    
    Returns:
        Statistics object
    """
    logger.info(
        "Statistics requested",
        extra={"user_id": user_id or "all"}
    )
    
    # TODO: Implement with database
    return {
        "total_resumes_generated": 0,
        "total_jobs_searched": 0,
        "average_compilation_time_ms": 0,
        "failed_compilations": 0,
        "successful_whatsapp_sends": 0,
        "avg_fit_score": 0.0
    }


@router.get("/errors")
async def get_recent_errors(limit: int = 50):
    """
    Get recent errors and failed jobs
    (Admin endpoint)
    """
    logger.info(
        "Recent errors requested",
        extra={"limit": limit}
    )
    
    # TODO: Implement with database dead-letter queue
    return {
        "total_errors": 0,
        "errors": [],
        "error_types": {
            "compilation": 0,
            "llm": 0,
            "search": 0,
            "notification": 0
        }
    }


@router.post("/errors/{error_id}/retry")
async def retry_failed_job(error_id: str):
    """
    Retry a failed job from dead-letter queue
    """
    logger.info(
        "Retry requested for failed job",
        extra={"error_id": error_id}
    )
    
    # TODO: Implement with database and orchestrator
    return {
        "status": "retry_queued",
        "error_id": error_id,
        "message": "Failed job has been re-queued for processing"
    }


@router.get("/config")
async def get_current_config():
    """
    Get current application configuration
    (Non-sensitive values only)
    """
    logger.debug("Configuration requested")
    
    from config.settings import settings
    
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "llm_model": settings.OLLAMA_MODEL,
        "scheduled_search_time": settings.SCHEDULED_SEARCH_TIME,
        "scheduled_search_query": settings.SCHEDULED_SEARCH_QUERY,
        "features": {
            "mem0_enabled": settings.ENABLE_MEM0,
            "langsmith_enabled": settings.ENABLE_LANGSMITH,
            "mock_mcp_tools": settings.USE_MOCK_MCP_TOOLS
        }
    }
