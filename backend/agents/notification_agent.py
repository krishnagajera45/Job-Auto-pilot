"""
Notification Agent - Sends job details and PDFs to user
Formats message and delivers via WhatsApp
"""

from models.core import AgentState
from mcp_tools.whatsapp_notifier_mcp import get_whatsapp_notifier_tool
from core.logger import get_logger

logger = get_logger("job_autopilot.agents.notification_agent")


class NotificationAgent:
    """
    Responsible for:
    - Formatting job summary message
    - Sending WhatsApp notification
    - Attaching generated PDFs
    - Logging application history
    """
    
    def __init__(self):
        self.whatsapp_tool = get_whatsapp_notifier_tool()
    
    async def invoke(self, state: AgentState) -> AgentState:
        """
        Send notification to user
        
        Args:
            state: Current agent state with resume_pdf_path
        
        Returns:
            Updated state with application_record
        """
        if not state.selected_job or not state.resume_pdf_path:
            logger.warning(
                "Missing required data for notification",
                extra={
                    "has_job": state.selected_job is not None,
                    "has_pdf": state.resume_pdf_path is not None
                }
            )
            state.errors.append("Missing job or PDF for notification")
            return state
        
        logger.info(
            "Notification Agent invoked",
            extra={
                "job_id": state.selected_job.id,
                "user_id": state.job_search_request.user_id
            }
        )
        
        try:
            job = state.selected_job
            curation = state.curation_result
            
            # Send WhatsApp notification
            message_id = await self.whatsapp_tool.send_job_notification(
                to_phone="+1234567890",  # Mock phone - replace with actual
                job_title=job.title,
                company=job.company,
                location=job.location,
                salary_range=job.salary_range,
                job_link=job.job_link,
                fit_score=curation.fit_score,
                resume_pdf_path=state.resume_pdf_path,
                cover_letter_pdf_path=state.cover_letter_pdf_path
            )
            
            logger.info(
                "WhatsApp notification sent",
                extra={
                    "message_id": message_id,
                    "job_id": job.id
                }
            )
            
            return state
        
        except Exception as e:
            logger.error(
                "Notification failed",
                extra={"error": str(e)},
                exc_info=True
            )
            state.errors.append(f"Notification error: {str(e)}")
            return state


def create_notification_agent() -> NotificationAgent:
    """Factory function to create Notification Agent"""
    return NotificationAgent()
