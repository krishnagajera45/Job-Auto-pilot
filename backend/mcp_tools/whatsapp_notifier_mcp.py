"""
WhatsApp Notifier MCP Tool for sending messages
"""

import asyncio
from typing import Optional, List
from config.settings import settings
from core.logger import get_logger

logger = get_logger("job_autopilot.mcp.whatsapp_notifier")


class WhatsAppNotificationError(Exception):
    """Raised when WhatsApp notification fails"""
    pass


class WhatsAppNotifierMCPTool:
    """
    MCP Tool wrapper for WhatsApp notifications
    Uses Twilio WhatsApp Business API
    """
    
    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock or settings.USE_MOCK_MCP_TOOLS
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER
        
        # Lazy import to avoid dependency issues
        self.twilio_client = None
        
        logger.info(
            "WhatsApp Notifier initialized",
            extra={
                "whatsapp_number": self.whatsapp_number,
                "use_mock": self.use_mock
            }
        )
    
    def _get_twilio_client(self):
        """Lazy load Twilio client"""
        if self.twilio_client is None and not self.use_mock:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(self.account_sid, self.auth_token)
            except ImportError:
                logger.warning("Twilio not installed, falling back to mock")
                self.use_mock = True
        
        return self.twilio_client
    
    async def send_message(
        self,
        to_phone: str,
        text: str,
        attachments: Optional[List[str]] = None
    ) -> str:
        """
        Send WhatsApp message
        
        Args:
            to_phone: Recipient phone number (WhatsApp format)
            text: Message text
            attachments: List of file paths to attach
        
        Returns:
            Message ID or success indicator
        
        Raises:
            WhatsAppNotificationError: If sending fails
        """
        logger.info(
            "Sending WhatsApp message",
            extra={
                "to_phone": to_phone,
                "text_length": len(text),
                "attachments_count": len(attachments or []),
                "use_mock": self.use_mock
            }
        )
        
        try:
            if self.use_mock:
                return await self._mock_send(to_phone, text, attachments)
            else:
                return await self._real_send(to_phone, text, attachments)
        
        except Exception as e:
            logger.error(
                "Failed to send WhatsApp message",
                extra={
                    "to_phone": to_phone,
                    "error": str(e)
                },
                exc_info=True
            )
            raise WhatsAppNotificationError(f"Failed to send WhatsApp message: {e}")
    
    async def _real_send(
        self,
        to_phone: str,
        text: str,
        attachments: Optional[List[str]] = None
    ) -> str:
        """
        Real Twilio WhatsApp API call
        """
        logger.debug(
            "Executing real WhatsApp send",
            extra={"to_phone": to_phone}
        )
        
        client = self._get_twilio_client()
        
        if client is None:
            logger.warning("Twilio client not available, using mock")
            return await self._mock_send(to_phone, text, attachments)
        
        try:
            # Format phone numbers for Twilio
            from_number = f"whatsapp:{self.whatsapp_number}"
            to_number = f"whatsapp:{to_phone}" if not to_phone.startswith("whatsapp:") else to_phone
            
            # Send message with attachments if provided
            if attachments:
                # Note: Twilio WhatsApp API has limitations on attachments
                # For production, consider uploading to cloud storage first
                message = client.messages.create(
                    from_=from_number,
                    to=to_number,
                    body=text,
                    media_url=attachments  # URLs to media files
                )
            else:
                message = client.messages.create(
                    from_=from_number,
                    to=to_number,
                    body=text
                )
            
            logger.info(
                "WhatsApp message sent",
                extra={
                    "to_phone": to_phone,
                    "message_id": message.sid
                }
            )
            
            return message.sid
        
        except Exception as e:
            raise WhatsAppNotificationError(f"Twilio API error: {e}")
    
    async def _mock_send(
        self,
        to_phone: str,
        text: str,
        attachments: Optional[List[str]] = None
    ) -> str:
        """
        Mock WhatsApp send for testing
        """
        logger.debug(
            "Using mock WhatsApp send",
            extra={
                "to_phone": to_phone,
                "text_preview": text[:50] + "..." if len(text) > 50 else text
            }
        )
        
        # Simulate network delay
        await asyncio.sleep(0.5)
        
        # Generate mock message ID
        message_id = f"mock_msg_{id(text):x}"
        
        # Log message content
        logger.debug(
            "Mock WhatsApp message logged",
            extra={
                "message_id": message_id,
                "to": to_phone,
                "body": text,
                "attachments": attachments or []
            }
        )
        
        return message_id
    
    async def send_job_notification(
        self,
        to_phone: str,
        job_title: str,
        company: str,
        location: str,
        salary_range: Optional[str],
        job_link: str,
        fit_score: float,
        resume_pdf_path: Optional[str] = None,
        cover_letter_pdf_path: Optional[str] = None
    ) -> str:
        """
        Send formatted job notification
        
        Args:
            to_phone: Recipient phone
            job_title: Job title
            company: Company name
            location: Job location
            salary_range: Salary range
            job_link: Link to job posting
            fit_score: Match score (0-100)
            resume_pdf_path: Path to resume PDF
            cover_letter_pdf_path: Path to cover letter PDF
        
        Returns:
            Message ID
        """
        # Format message
        message = f"""📋 *New Job Match!*

🏢 *{company}*
💼 *{job_title}*
📍 {location}
💰 {salary_range or 'Competitive'}

✨ *Fit Score:* {fit_score:.0f}%

🔗 *Link:* {job_link}

Your tailored resume and cover letter are attached!

---
Generated by Job Autopilot 🚀
"""
        
        # Collect attachments
        attachments = []
        if resume_pdf_path:
            attachments.append(resume_pdf_path)
        if cover_letter_pdf_path:
            attachments.append(cover_letter_pdf_path)
        
        return await self.send_message(to_phone, message, attachments or None)


# Singleton instance
_whatsapp_notifier_tool = None


def get_whatsapp_notifier_tool() -> WhatsAppNotifierMCPTool:
    """Get WhatsApp Notifier MCP tool instance"""
    global _whatsapp_notifier_tool
    if _whatsapp_notifier_tool is None:
        _whatsapp_notifier_tool = WhatsAppNotifierMCPTool()
    return _whatsapp_notifier_tool
