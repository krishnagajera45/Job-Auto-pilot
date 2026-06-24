"""
Scheduled Trigger Handler - Executes scheduled job searches
Uses APScheduler for cron jobs
"""

from fastapi import APIRouter, BackgroundTasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from models.core import InputSource
from agents.orchestrator import run_workflow
from config.settings import settings
from core.logger import get_logger

logger = get_logger("job_autopilot.api.scheduled_trigger")

router = APIRouter(prefix="/api", tags=["scheduled"])

# Global scheduler instance
_scheduler: AsyncIOScheduler = None


class ScheduledTriggerManager:
    """
    Manages scheduled job searches
    """
    
    def __init__(self):
        self.scheduler = None
        self.scheduled_query = settings.SCHEDULED_SEARCH_QUERY
        self.scheduled_time = settings.SCHEDULED_SEARCH_TIME
    
    async def initialize(self):
        """Initialize scheduler"""
        logger.info(
            "Initializing scheduler",
            extra={
                "scheduled_time": self.scheduled_time,
                "scheduled_query": self.scheduled_query
            }
        )
        
        self.scheduler = AsyncIOScheduler()
        
        # Parse scheduled time (HH:MM format)
        hour, minute = self._parse_time(self.scheduled_time)
        
        # Schedule daily job search at specified time
        self.scheduler.add_job(
            self._run_scheduled_search,
            trigger=CronTrigger(hour=hour, minute=minute),
            id="daily_job_search",
            name="Daily Job Search",
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Scheduler initialized and started")
    
    async def shutdown(self):
        """Shutdown scheduler"""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("Scheduler shutdown")
    
    async def _run_scheduled_search(self):
        """Execute scheduled job search"""
        logger.info(
            "Executing scheduled job search",
            extra={"query": self.scheduled_query}
        )
        
        try:
            # Use system user ID for scheduled searches
            system_user_id = "system_scheduled_search"
            
            result = await run_workflow(
                query=self.scheduled_query,
                user_id=system_user_id,
                input_source=InputSource.SCHEDULED
            )
            
            if result.errors:
                logger.warning(
                    "Scheduled search completed with errors",
                    extra={"errors": result.errors}
                )
            else:
                logger.info(
                    "Scheduled search completed successfully",
                    extra={
                        "jobs_found": len(result.job_postings),
                        "has_pdf": result.resume_pdf_path is not None
                    }
                )
        
        except Exception as e:
            logger.error(
                "Scheduled search failed",
                extra={"error": str(e)},
                exc_info=True
            )
    
    @staticmethod
    def _parse_time(time_str: str) -> tuple:
        """
        Parse time string in HH:MM format
        Returns (hour, minute) tuple
        """
        parts = time_str.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid time format: {time_str}. Use HH:MM")
        
        try:
            hour = int(parts[0])
            minute = int(parts[1])
            
            if not (0 <= hour <= 23):
                raise ValueError(f"Hour must be 0-23, got {hour}")
            if not (0 <= minute <= 59):
                raise ValueError(f"Minute must be 0-59, got {minute}")
            
            return hour, minute
        
        except ValueError as e:
            raise ValueError(f"Invalid time format: {time_str}. {str(e)}")


# Global trigger manager instance
_trigger_manager = ScheduledTriggerManager()


async def initialize_scheduler():
    """Initialize the scheduler (call this on app startup)"""
    await _trigger_manager.initialize()


async def shutdown_scheduler():
    """Shutdown the scheduler (call this on app shutdown)"""
    await _trigger_manager.shutdown()


@router.post("/trigger-search")
async def manual_trigger_search(background_tasks: BackgroundTasks):
    """
    Manually trigger scheduled search
    Useful for testing or immediate execution
    """
    logger.info("Manual scheduled search trigger requested")
    
    # Add to background tasks
    background_tasks.add_task(
        _trigger_manager._run_scheduled_search
    )
    
    return {
        "status": "triggered",
        "message": "Scheduled search initiated",
        "query": _trigger_manager.scheduled_query
    }


@router.get("/trigger-search/status")
async def get_scheduler_status():
    """
    Get status of scheduler
    """
    logger.debug("Scheduler status check requested")
    
    return {
        "scheduler_running": _trigger_manager.scheduler is not None and _trigger_manager.scheduler.running,
        "next_run": str(_trigger_manager.scheduler.get_job("daily_job_search").next_run_time)
        if _trigger_manager.scheduler and _trigger_manager.scheduler.get_job("daily_job_search")
        else None,
        "scheduled_time": _trigger_manager.scheduled_time,
        "scheduled_query": _trigger_manager.scheduled_query
    }


@router.post("/trigger-search/update-query")
async def update_scheduled_query(query: str):
    """
    Update the hardcoded scheduled query
    """
    logger.info(
        "Scheduled query update requested",
        extra={"new_query": query}
    )
    
    _trigger_manager.scheduled_query = query
    
    return {
        "status": "updated",
        "message": "Scheduled query updated",
        "new_query": query
    }


@router.post("/trigger-search/update-time")
async def update_scheduled_time(time: str):
    """
    Update the scheduled search time
    Format: HH:MM (e.g., "12:00")
    """
    logger.info(
        "Scheduled time update requested",
        extra={"new_time": time}
    )
    
    try:
        hour, minute = _trigger_manager._parse_time(time)
        _trigger_manager.scheduled_time = time
        
        # Update scheduler job
        if _trigger_manager.scheduler:
            _trigger_manager.scheduler.remove_job("daily_job_search")
            _trigger_manager.scheduler.add_job(
                _trigger_manager._run_scheduled_search,
                trigger=CronTrigger(hour=hour, minute=minute),
                id="daily_job_search",
                name="Daily Job Search"
            )
        
        return {
            "status": "updated",
            "message": "Scheduled time updated",
            "new_time": time
        }
    
    except ValueError as e:
        logger.warning(
            "Invalid time format",
            extra={"time": time, "error": str(e)}
        )
        return {
            "status": "error",
            "message": str(e)
        }
