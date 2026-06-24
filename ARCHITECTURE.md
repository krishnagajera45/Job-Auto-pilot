# Job Autopilot - Architecture & Design Document

## 1. System Overview

Job Autopilot is a **multi-agent agentic AI system** orchestrated using LangGraph that automates the entire job application workflow:
1. Search job boards
2. Curate matches with user skills
3. Generate tailored LaTeX resumes
4. Compile PDFs
5. Deliver via WhatsApp

### Design Principles
- **Async-first**: All I/O operations are non-blocking using `asyncio`
- **Modular**: Each agent is independent and testable
- **Error-resilient**: Self-correcting mechanisms for LaTeX compilation
- **Observable**: Full traceability in LangSmith
- **Local-first**: Ollama for LLM, Mem0 for memory, no external API dependencies except Brave Search

---

## 2. Workflow Architecture

### State Machine (LangGraph)

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENTRY POINT                               │
│              (WhatsApp/Link/Scheduled Trigger)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  INPUT DISPATCHER                                │
│                                                                   │
│  • Parse WhatsApp message → Extract query                       │
│  • Extract job link → Fetch description                         │
│  • Scheduled trigger → Load hardcoded query                     │
│                                                                   │
│  Output: Normalized JobSearchRequest                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
        ┌──────────────────┐   ┌──────────────────┐
        │ JOB SEARCH AGENT │   │  JOB PARSER AGENT│
        │ (Brave Search)   │   │ (Link Extraction)│
        └──────────────────┘   └──────────────────┘
                    │                 │
                    └────────┬────────┘
                             │
                             ▼
        ┌─────────────────────────────────────────┐
        │      CURATION AGENT                      │
        │                                          │
        │  • Query Mem0 for user skills          │
        │  • Analyze job requirements             │
        │  • Rank fit (relevance score)           │
        │  • Select template (SWE/DevOps/ML)     │
        │                                          │
        │  Output: CurationResult with template   │
        └─────────────────────────────────────────┘
                             │
                             ▼
        ┌─────────────────────────────────────────┐
        │  RESUME GENERATION AGENT                │
        │                                          │
        │  • LLM generates LaTeX from template   │
        │  • Tailored to job description         │
        │  • Pure LaTeX (no markdown)            │
        │                                          │
        │  Output: LaTeX code (.tex)             │
        └─────────────────────────────────────────┘
                             │
                             ▼
        ┌─────────────────────────────────────────┐
        │  COVER LETTER GENERATION AGENT          │
        │                                          │
        │  • LLM generates cover letter          │
        │  • Specific to job + company           │
        │  • Pure LaTeX format                   │
        │                                          │
        │  Output: Cover letter LaTeX code       │
        └─────────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
        ┌──────────────────┐  ┌──────────────────┐
        │ COMPILATION AGENT│  │ COMPILATION AGENT│
        │  (Resume PDF)    │  │ (Cover Letter)   │
        └──────────────────┘  └──────────────────┘
                    │                 │
                    │  (with retry &  │
                    │   self-correct) │
                    │                 │
                    └────────┬────────┘
                             │
                             ▼
        ┌─────────────────────────────────────────┐
        │  NOTIFICATION AGENT                     │
        │                                          │
        │  • Format job summary                  │
        │  • Prepare WhatsApp message            │
        │  • Send job link + PDFs                │
        │  • Log in database                     │
        │                                          │
        │  Output: Message sent to user          │
        └─────────────────────────────────────────┘
```

### Data Flow (Detailed)

```
User Input (WhatsApp/Link/Scheduled)
    ↓
Input Router
    ├─→ WhatsApp: extract_query_from_message()
    ├─→ Link: fetch_and_parse_job_description()
    └─→ Scheduled: load_hardcoded_query()
    ↓
JobSearchRequest {
    query: str,
    user_id: str,
    input_source: "whatsapp" | "link" | "scheduled",
    original_message: str (optional)
}
    ↓
Job Search Agent
    ├─→ Call Brave Search MCP
    └─→ Parse results
    ↓
List[JobPosting] {
    title: str,
    company: str,
    description: str,
    location: str,
    salary_range: Optional[str],
    job_link: str
}
    ↓
Curation Agent
    ├─→ Query Mem0: get_user_profile(user_id)
    ├─→ Analyze: score_fit(job, user_profile)
    └─→ Select: choose_template(job_type)
    ↓
CurationResult {
    selected_job: JobPosting,
    fit_score: float,
    template_type: "SWE" | "DevOps" | "ML",
    user_skills: List[str],
    key_requirements: List[str]
}
    ↓
Resume Generation Agent
    ├─→ LLM: generate_latex_resume(
    │   template,
    │   job,
    │   user_skills,
    │   key_requirements
    │)
    └─→ Output: LaTeX code
    ↓
Compilation Agent
    ├─→ write_tex_file(latex_code)
    ├─→ pdflatex compilation
    ├─→ If error:
    │   └─→ LLM error analysis + fix
    │   └─→ Retry (max 3 attempts)
    └─→ Output: PDF file path
    ↓
Notification Agent
    ├─→ Prepare WhatsApp message
    ├─→ Upload PDF to storage
    └─→ Send via Twilio
    ↓
User receives WhatsApp message + PDF
```

---

## 3. Agent Specifications

### 3.1 Job Search Agent

**Input**: `JobSearchRequest`
**Output**: `List[JobPosting]`

```python
class JobSearchAgent:
    """
    Responsible for:
    - Executing Brave Search queries
    - Parsing job posting results
    - Structuring job data
    - Handling pagination (10-15 results)
    """
    
    async def invoke(self, request: JobSearchRequest) -> List[JobPosting]:
        # 1. Call BraveSearch MCP
        # 2. Parse HTML/JSON responses
        # 3. Extract: title, company, description, location, salary, link
        # 4. Return structured list
        pass
```

**Error Handling**:
- If Brave Search fails: Retry with exponential backoff (3 attempts)
- If parsing fails: Skip result, continue
- If no results: Return empty list, notify user

### 3.2 Job Parser Agent

**Input**: `job_url: str`
**Output**: `JobPosting`

```python
class JobParserAgent:
    """
    Responsible for:
    - Fetching page from URL
    - Extracting job description
    - Cleaning and parsing HTML
    - Structuring job data
    """
    
    async def invoke(self, job_url: str) -> JobPosting:
        # 1. Fetch URL
        # 2. Parse with BeautifulSoup/Selenium
        # 3. Extract job info
        # 4. Return structured data
        pass
```

### 3.3 Curation Agent

**Input**: `JobPosting`, `UserProfile` (from Mem0)
**Output**: `CurationResult`

```python
class CurationAgent:
    """
    Responsible for:
    - Querying Mem0 for user skills/experience
    - Analyzing job requirements
    - Computing job-fit score
    - Selecting appropriate LaTeX template
    - Identifying key requirements to highlight
    """
    
    async def invoke(self, job: JobPosting) -> CurationResult:
        # 1. Get user_profile from Mem0
        # 2. Compute relevance_score (LLM or heuristic)
        # 3. Select template based on job type
        # 4. Extract key_requirements matching user skills
        # 5. Return curation result
        pass
```

**Mem0 Integration**:
```python
# Query Mem0 for user context
user_profile = mem0.search(
    query="My skills, experience, and past roles",
    user_id=request.user_id
)
# Result includes: skills, experience, past_roles, certifications, etc.
```

### 3.4 Resume Generation Agent

**Input**: `CurationResult`, `JobPosting`, `LaTeX Template`
**Output**: `str` (LaTeX code)

```python
class ResumeGenerationAgent:
    """
    Responsible for:
    - Generating role-specific LaTeX resume
    - Tailoring content to job description
    - Ensuring valid LaTeX syntax
    - No markdown wrappers
    """
    
    STRICT_PROMPT = """
    You are a LaTeX expert. Generate a professional resume in pure LaTeX format.
    
    Requirements:
    - Output ONLY valid LaTeX code, NO markdown
    - Use the provided template as base
    - Tailor experience bullets to job description
    - Highlight skills matching: {key_requirements}
    - ATS-optimized formatting
    - No comments explaining code
    
    Template:
    {template}
    
    Job Description:
    {job_description}
    
    User Profile:
    {user_profile}
    
    Output ONLY the LaTeX code, nothing else.
    """
    
    async def invoke(self, curation: CurationResult) -> str:
        # 1. Load template
        # 2. Construct prompt with strict instructions
        # 3. Call LLM
        # 4. Validate LaTeX output
        # 5. Return LaTeX code
        pass
```

**Prompt Engineering**:
- Enforce NO markdown wrappers
- Explicit instruction: "Output ONLY the LaTeX code"
- Include template as example
- Include key requirements to highlight
- Use CoT (Chain of Thought): "You are a LaTeX expert..."

### 3.5 Cover Letter Generation Agent

**Input**: `JobPosting`, `UserProfile` (Mem0), `CurationResult`
**Output**: `str` (LaTeX code)

```python
class CoverLetterGenerationAgent:
    """
    Responsible for:
    - Generating role-specific cover letter
    - LaTeX formatted
    - Personalized to job and company
    """
    
    async def invoke(self, curation: CurationResult) -> str:
        # 1. LLM generates personalized cover letter
        # 2. Format as LaTeX
        # 3. Return LaTeX code
        pass
```

### 3.6 Compilation Agent

**Input**: `LaTeX code: str`, `filename: str`
**Output**: `str` (PDF file path)

```python
class CompilationAgent:
    """
    Responsible for:
    - Writing LaTeX to .tex file
    - Calling pdflatex
    - Error handling with self-correction
    - Retry mechanism
    """
    
    MAX_RETRIES = 3
    
    async def invoke(self, latex_code: str, filename: str) -> str:
        for attempt in range(self.MAX_RETRIES):
            try:
                # 1. Write .tex file
                tex_path = f"/tmp/{filename}.tex"
                write_tex_file(tex_path, latex_code)
                
                # 2. Call pdflatex MCP
                pdf_path = await self.latex_mcp.compile(tex_path)
                
                # 3. Verify PDF exists
                if os.path.exists(pdf_path):
                    return pdf_path
                    
            except LaTeXCompilationError as e:
                # 4. LLM analyzes error and fixes LaTeX
                error_msg = str(e)
                fixed_latex = await self.llm.invoke(f"""
                    The LaTeX compilation failed with this error:
                    {error_msg}
                    
                    Original LaTeX:
                    {latex_code}
                    
                    Fix the LaTeX code and return ONLY the corrected code.
                """)
                latex_code = fixed_latex
                
                if attempt == self.MAX_RETRIES - 1:
                    raise CompilationFailedError(
                        f"LaTeX compilation failed after {self.MAX_RETRIES} attempts"
                    )
        
        raise CompilationFailedError("Unknown error")
```

### 3.7 Notification Agent

**Input**: `JobPosting`, `pdf_resume_path: str`, `pdf_cover_letter_path: str`
**Output**: `bool` (success)

```python
class NotificationAgent:
    """
    Responsible for:
    - Formatting job summary
    - Sending WhatsApp message
    - Attaching PDFs
    - Logging application history
    """
    
    async def invoke(
        self,
        job: JobPosting,
        resume_pdf: str,
        cover_letter_pdf: str,
        user_phone: str
    ) -> bool:
        # 1. Format message
        message = f"""
        📋 New Job Match!
        
        🏢 {job.company}
        💼 {job.title}
        📍 {job.location}
        💰 {job.salary_range or 'Competitive'}
        
        ✨ Fit Score: 95%
        🔗 Link: {job.job_link}
        
        Your tailored resume and cover letter are attached!
        """
        
        # 2. Send via WhatsApp MCP
        await self.whatsapp_mcp.send_message(
            phone=user_phone,
            text=message,
            attachments=[resume_pdf, cover_letter_pdf]
        )
        
        # 3. Log in database
        await self.db.create_application(
            user_id=user_id,
            job_id=job.id,
            resume_pdf=resume_pdf,
            cover_letter_pdf=cover_letter_pdf,
            status="sent",
            timestamp=datetime.now()
        )
        
        return True
```

---

## 4. MCP Tool Specifications

### 4.1 Brave Search MCP

```python
class BraveSearchMCP:
    """
    MCP Tool for job search using Brave Search API
    
    Parameters:
    - query: str (e.g., "Python SDE roles in San Francisco")
    - count: int (number of results, default 10-15)
    - offset: int (pagination)
    
    Returns:
    - List of job postings with parsed metadata
    """
    
    async def search(query: str, count: int = 10) -> List[Dict]:
        # Call Brave Search API
        # Parse results
        # Return structured data
        pass
```

### 4.2 LaTeX Compiler MCP

```python
class LaTeXCompilerMCP:
    """
    MCP Tool for compiling LaTeX to PDF
    
    Parameters:
    - tex_file_path: str
    
    Returns:
    - PDF file path
    
    Raises:
    - LaTeXCompilationError with error details
    """
    
    async def compile(tex_file_path: str) -> str:
        # Call pdflatex subprocess
        # Handle errors
        # Return PDF path or raise error
        pass
```

### 4.3 WhatsApp Notifier MCP

```python
class WhatsAppNotifierMCP:
    """
    MCP Tool for sending WhatsApp messages
    
    Parameters:
    - phone: str (phone number)
    - text: str (message body)
    - attachments: List[str] (file paths)
    
    Returns:
    - Message ID or raises error
    """
    
    async def send_message(
        phone: str,
        text: str,
        attachments: List[str] = None
    ) -> str:
        # Call Twilio WhatsApp API
        # Handle errors
        # Return message ID
        pass
```

---

## 5. Data Models

### Core Models

```python
class JobPosting(BaseModel):
    id: str
    title: str
    company: str
    description: str
    location: str
    salary_range: Optional[str]
    job_link: str
    posted_date: datetime
    source: str  # "brave_search" or "direct_link"

class UserProfile(BaseModel):
    user_id: str
    name: str
    skills: List[str]
    experience: List[Dict]  # {role, company, duration}
    education: List[Dict]   # {degree, school}
    certifications: List[str]
    preferences: Dict       # {preferred_roles, locations, etc}

class CurationResult(BaseModel):
    selected_job: JobPosting
    fit_score: float        # 0-100
    template_type: str      # "SWE", "DevOps", "ML"
    user_skills: List[str]
    key_requirements: List[str]

class ApplicationRecord(BaseModel):
    id: str
    user_id: str
    job_id: str
    resume_pdf_path: str
    cover_letter_pdf_path: str
    status: str             # "generated", "sent", "applied", "rejected"
    created_at: datetime
    sent_at: Optional[datetime]
```

---

## 6. Input Handlers

### 6.1 WhatsApp Webhook Handler

```
User sends: "Find me SDE roles in NYC"
    ↓
WhatsApp → Twilio → FastAPI webhook
    ↓
parse_whatsapp_message(message) → extract intent + parameters
    ↓
JobSearchRequest {
    query: "SDE roles in NYC",
    user_id: extracted from phone,
    input_source: "whatsapp",
    original_message: "Find me SDE roles in NYC"
}
    ↓
Trigger orchestrator
```

### 6.2 Direct Job Link Handler

```
User POSTs: {job_link: "https://linkedin.com/jobs/123456"}
    ↓
Validate URL and fetch job description
    ↓
JobPosting populated from page content
    ↓
Trigger orchestrator (skip search agent)
```

### 6.3 Scheduled Trigger

```
APScheduler: Every day at 12:00 PM
    ↓
Load hardcoded query from config:
    SCHEDULED_SEARCH_QUERY = "SDE roles in tech hubs"
    ↓
JobSearchRequest {
    query: "SDE roles in tech hubs",
    user_id: system_user_id,
    input_source: "scheduled"
}
    ↓
Trigger orchestrator
    ↓
Results aggregated and sent to user
```

---

## 7. Error Handling Strategy

### Retry Logic

```python
async def retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0
):
    """Exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            await asyncio.sleep(delay)
```

### Dead Letter Queue

```python
# Failed jobs stored in dead-letter queue
# Admin dashboard shows failed jobs
# Manual retry option available
# Notifications sent to admin for critical failures
```

### LaTeX Self-Correction

```
pdflatex compilation fails
    ↓
Extract error message
    ↓
LLM: "Fix this LaTeX error: {error_message}"
    ↓
Retry compilation (max 3 attempts)
    ↓
If still fails: Mark as failed, notify user
```

---

## 8. Logging & Observability

### LangSmith Integration

Every agent call is traced:
```python
from langsmith import trace

@trace(name="job_search_agent")
async def search_jobs(request: JobSearchRequest):
    # Automatically logged to LangSmith
    pass
```

### Structured Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info(
    "Resume generated",
    extra={
        "job_id": job.id,
        "user_id": user_id,
        "template_type": template_type,
        "compilation_attempts": 2
    }
)
```

### Metrics

- **Agent execution time**: latency per agent
- **Compilation retry count**: avg retries for LaTeX
- **Success rate**: % of jobs processed end-to-end
- **Mem0 query latency**: time to retrieve user profile
- **WhatsApp delivery**: message sent vs received

---

## 9. Database Schema

### Tables

```sql
-- Users
CREATE TABLE users (
    id PRIMARY KEY,
    username UNIQUE,
    phone UNIQUE,
    hashed_password,
    created_at
);

-- User Preferences
CREATE TABLE user_preferences (
    id PRIMARY KEY,
    user_id FOREIGN KEY,
    preferred_roles TEXT,
    preferred_locations TEXT,
    preferred_companies TEXT,
    remote_only BOOLEAN
);

-- Job Postings (cached)
CREATE TABLE job_postings (
    id PRIMARY KEY,
    title,
    company,
    description TEXT,
    location,
    salary_range,
    job_link UNIQUE,
    source,
    posted_date,
    scraped_date
);

-- Application Records
CREATE TABLE applications (
    id PRIMARY KEY,
    user_id FOREIGN KEY,
    job_id FOREIGN KEY,
    resume_pdf_path,
    cover_letter_pdf_path,
    fit_score,
    status,
    created_at,
    sent_at,
    user_feedback
);

-- Failed Jobs (Dead Letter)
CREATE TABLE failed_jobs (
    id PRIMARY KEY,
    job_posting_id FOREIGN KEY,
    user_id FOREIGN KEY,
    error_message TEXT,
    retry_count,
    last_attempted_at,
    failed_at
);
```

---

## 10. Deployment Architecture

### Docker Compose Stack

```yaml
services:
  ollama:
    image: ollama/ollama
    ports: [11434:11434]
    environment:
      - OLLAMA_MODELS=gemma2

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=job_autopilot
      - POSTGRES_PASSWORD=...

  fastapi:
    build: ./backend
    ports: [8000:8000]
    depends_on:
      - ollama
      - postgres
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - DATABASE_URL=postgresql://...

  redis:
    image: redis:7
    ports: [6379:6379]
```

### Environment Variables

```
# Ollama LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma2

# APIs
BRAVE_SEARCH_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=...

# Mem0
MEM0_API_KEY=...

# LangSmith
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=job-autopilot

# Database
DATABASE_URL=postgresql://...

# Scheduler
SCHEDULED_SEARCH_TIME=12:00
SCHEDULED_SEARCH_QUERY=SDE roles in major tech hubs
```

---

## 11. Development Workflow

### Local Testing

```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: FastAPI
cd backend && python main.py

# Terminal 3: Test WhatsApp webhook
curl -X POST http://localhost:8000/api/whatsapp/webhook \
  -H "Content-Type: application/json" \
  -d '{"From": "whatsapp:+1234567890", "Body": "Find SDE roles"}'
```

### Debugging

- LangSmith traces: Full visibility into agent decisions
- Structured logs: Search logs by user_id, job_id, error_type
- Database inspection: Query failed_jobs table
- Mock MCP tools: Test agents without external APIs

---

## 12. Future Enhancements

- **Multi-source scraping**: Indeed, Glassdoor, Stack Overflow Jobs
- **LinkedIn auto-apply**: Automatically apply using LinkedIn API
- **Salary negotiation agent**: Coaching based on market data
- **Interview prep agent**: Generate technical interview questions
- **Email outreach**: Send cold emails to recruiters
- **Resume version control**: Track all generated resumes with versioning
- **Analytics dashboard**: User insights, job match trends
- **Mobile app**: React Native for mobile notifications

---

## Summary

Job Autopilot follows a **pipeline architecture** with clear separation of concerns:

1. **Input** → Router determines source (WhatsApp/Link/Scheduled)
2. **Search** → Fetches job postings from Brave Search or direct link
3. **Curation** → Analyzes fit and selects template using Mem0
4. **Generation** → LLM generates LaTeX resume and cover letter
5. **Compilation** → pdflatex compiles to PDF with error recovery
6. **Notification** → Sends results to user via WhatsApp

Every step is **async**, **observable**, and **resilient** to failures.
