"""
Core data models for Job Autopilot
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Literal
from datetime import datetime
from enum import Enum


class InputSource(str, Enum):
    """Input source for job processing"""
    WHATSAPP = "whatsapp"
    JOB_LINK = "job_link"
    SCHEDULED = "scheduled"


class JobSource(str, Enum):
    """Job search source/provider"""
    BRAVE_SEARCH = "brave_search"
    OPENCLAW = "openclaw"
    BOTH = "both"  # Use both sources and combine results


class JobPosting(BaseModel):
    """Represents a job posting"""
    id: str
    title: str
    company: str
    description: str
    location: str
    salary_range: Optional[str] = None
    job_link: str
    posted_date: datetime
    source: str  # "brave_search", "linkedin", "indeed", etc.
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "job_123",
                "title": "Senior Software Engineer",
                "company": "Google",
                "description": "Looking for experienced SDE...",
                "location": "Mountain View, CA",
                "salary_range": "$200k - $300k",
                "job_link": "https://google.com/careers/job_123",
                "posted_date": "2024-01-15T10:00:00",
                "source": "brave_search"
            }
        }


class UserProfile(BaseModel):
    """User profile from Mem0"""
    user_id: str
    name: str
    skills: List[str] = Field(default_factory=list)
    experience: List[Dict] = Field(default_factory=list)  # [{role, company, duration, description}]
    education: List[Dict] = Field(default_factory=list)   # [{degree, school, year}]
    certifications: List[str] = Field(default_factory=list)
    preferences: Optional[Dict] = Field(default_factory=dict)  # {preferred_roles, locations, etc}


class TemplateType(str, Enum):
    """LaTeX resume template types"""
    SWE = "swe"
    DEVOPS = "devops"
    ML = "ml"


class CurationResult(BaseModel):
    """Result from curation agent"""
    selected_job: JobPosting
    fit_score: float = Field(ge=0, le=100, description="Job fit score 0-100")
    template_type: TemplateType
    user_skills: List[str]
    key_requirements: List[str]  # Requirements matching user skills


class ApplicationStatus(str, Enum):
    """Status of job application"""
    GENERATED = "generated"
    SENT = "sent"
    APPLIED = "applied"
    REJECTED = "rejected"
    ACCEPTED = "accepted"


class ApplicationRecord(BaseModel):
    """Record of generated resume + application"""
    id: str
    user_id: str
    job_id: str
    resume_pdf_path: str
    cover_letter_pdf_path: str
    fit_score: float
    status: ApplicationStatus
    created_at: datetime
    sent_at: Optional[datetime] = None
    user_feedback: Optional[str] = None


class JobSearchRequest(BaseModel):
    """Request to search for jobs"""
    query: str = Field(description="Search query, e.g., 'SDE roles in NYC'")
    user_id: str
    input_source: InputSource
    job_source: JobSource = Field(
        default=JobSource.BRAVE_SEARCH,
        description="Job search provider: 'brave_search', 'openclaw', or 'both'"
    )
    original_message: Optional[str] = None  # For WhatsApp context


class JobLinkSubmission(BaseModel):
    """User submitting a job link directly"""
    job_link: str = Field(description="Full URL to job posting")
    user_id: str


class ResumeGenerationResponse(BaseModel):
    """Response from resume generation"""
    resume_pdf_path: str
    cover_letter_pdf_path: str
    job_id: str
    application_id: str
    message: str = "Resume and cover letter generated successfully"


class FailedJob(BaseModel):
    """Failed job record for dead-letter queue"""
    id: str
    job_posting_id: str
    user_id: str
    error_message: str
    error_type: str  # "compilation", "llm", "search", "notification"
    retry_count: int
    last_attempted_at: datetime
    failed_at: datetime


class AgentState(BaseModel):
    """State passed between agents in LangGraph"""
    job_search_request: JobSearchRequest
    job_postings: List[JobPosting] = Field(default_factory=list)
    selected_job: Optional[JobPosting] = None
    curation_result: Optional[CurationResult] = None
    resume_latex: Optional[str] = None
    cover_letter_latex: Optional[str] = None
    resume_pdf_path: Optional[str] = None
    cover_letter_pdf_path: Optional[str] = None
    application_record: Optional[ApplicationRecord] = None
    errors: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
