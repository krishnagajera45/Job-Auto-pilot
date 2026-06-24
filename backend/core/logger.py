"""
Structured logging for Job Autopilot with LangSmith integration
"""

import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime
from config.settings import settings


# Configure root logger
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("job_autopilot.log")
    ]
)


class StructuredLogger:
    """
    Structured logging with support for context and LangSmith integration
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs):
        """Set context for all subsequent logs"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear all context"""
        self.context.clear()
    
    def _format_extra(self, extra: Optional[Dict] = None) -> Dict:
        """Merge context with extra fields"""
        merged = {**self.context}
        if extra:
            merged.update(extra)
        return merged
    
    def info(self, message: str, extra: Optional[Dict] = None):
        """Log info message"""
        self.logger.info(
            message,
            extra=self._format_extra(extra)
        )
    
    def debug(self, message: str, extra: Optional[Dict] = None):
        """Log debug message"""
        self.logger.debug(
            message,
            extra=self._format_extra(extra)
        )
    
    def warning(self, message: str, extra: Optional[Dict] = None):
        """Log warning message"""
        self.logger.warning(
            message,
            extra=self._format_extra(extra)
        )
    
    def error(self, message: str, extra: Optional[Dict] = None, exc_info: bool = True):
        """Log error message"""
        self.logger.error(
            message,
            extra=self._format_extra(extra),
            exc_info=exc_info
        )
    
    def critical(self, message: str, extra: Optional[Dict] = None, exc_info: bool = True):
        """Log critical message"""
        self.logger.critical(
            message,
            extra=self._format_extra(extra),
            exc_info=exc_info
        )


# Create logger instances for each module
def get_logger(name: str) -> StructuredLogger:
    """Get or create a logger instance"""
    return StructuredLogger(name)


# Pre-created loggers for common modules
logger = get_logger("job_autopilot")
agents_logger = get_logger("job_autopilot.agents")
mcp_logger = get_logger("job_autopilot.mcp")
api_logger = get_logger("job_autopilot.api")


# Export for convenience
__all__ = [
    "logger",
    "agents_logger",
    "mcp_logger",
    "api_logger",
    "get_logger",
    "StructuredLogger"
]
