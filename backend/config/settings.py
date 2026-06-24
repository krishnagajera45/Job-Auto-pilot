"""
Configuration settings for Job Autopilot
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # ==========================
    # LLM Configuration (Ollama)
    # ==========================
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434",
        description="Ollama base URL"
    )
    OLLAMA_MODEL: str = Field(
        default="gemma2",
        description="Ollama model name"
    )
    
    # ==========================
    # API Keys & External Services
    # ==========================
    BRAVE_SEARCH_API_KEY: str = Field(
        default="brave_search_test_key_12345",
        description="Brave Search API key"
    )
    
    TWILIO_ACCOUNT_SID: str = Field(
        default="AC_test_account_sid_12345",
        description="Twilio account SID"
    )
    TWILIO_AUTH_TOKEN: str = Field(
        default="twilio_auth_token_12345",
        description="Twilio auth token"
    )
    TWILIO_WHATSAPP_NUMBER: str = Field(
        default="+1234567890",
        description="Twilio WhatsApp number"
    )
    
    MEM0_API_KEY: str = Field(
        default="mem0_test_key_12345",
        description="Mem0 API key for memory management"
    )
    
    LANGSMITH_API_KEY: Optional[str] = Field(
        default=None,
        description="LangSmith API key for observability"
    )
    LANGSMITH_PROJECT: str = Field(
        default="job-autopilot",
        description="LangSmith project name"
    )
    
    # ==========================
    # Database
    # ==========================
    DATABASE_URL: str = Field(
        default="sqlite:///./job_autopilot.db",
        description="Database connection URL"
    )
    
    # ==========================
    # Scheduling
    # ==========================
    SCHEDULED_SEARCH_TIME: str = Field(
        default="12:00",
        description="Time to run scheduled search (HH:MM format)"
    )
    SCHEDULED_SEARCH_QUERY: str = Field(
        default="Senior Software Engineer roles in tech hubs",
        description="Hardcoded query for scheduled searches"
    )
    
    # ==========================
    # Application
    # ==========================
    APP_NAME: str = "Job Autopilot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # ==========================
    # Paths
    # ==========================
    OUTPUT_DIR: str = Field(
        default="./output",
        description="Directory for generated PDFs"
    )
    TEMPLATE_DIR: str = Field(
        default="./config/templates",
        description="Directory for LaTeX templates"
    )
    
    # ==========================
    # Feature Flags
    # ==========================
    ENABLE_MEM0: bool = Field(default=True, description="Enable Mem0 integration")
    ENABLE_LANGSMITH: bool = Field(default=True, description="Enable LangSmith tracing")
    USE_MOCK_MCP_TOOLS: bool = Field(
        default=True,
        description="Use mock MCP tools for testing (no real API calls)"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
