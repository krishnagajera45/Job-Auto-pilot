# Job Autopilot - API Reference

## Base URL

```
http://localhost:8000
```

## Endpoints Overview

### Health & Status
- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `GET /api/stats` - Get statistics
- `GET /api/config` - Get configuration

### WhatsApp Integration
- `POST /api/whatsapp/webhook` - Receive WhatsApp messages
- `GET /api/whatsapp/webhook` - Webhook verification

### Job Link Submission
- `POST /api/job-link` - Submit job link
- `GET /api/job-link/status/{request_id}` - Get submission status

### Scheduled Searches
- `POST /api/trigger-search` - Manually trigger scheduled search
- `GET /api/trigger-search/status` - Get scheduler status
- `POST /api/trigger-search/update-query` - Update scheduled query
- `POST /api/trigger-search/update-time` - Update scheduled time

### Application Tracking
- `GET /api/status/{job_id}` - Get job status
- `GET /api/resumes` - List generated resumes
- `GET /api/applications` - List applications
- `GET /api/errors` - Get recent errors
- `POST /api/errors/{error_id}/retry` - Retry failed job

---

## Detailed Endpoints

### WhatsApp Webhook

#### POST /api/whatsapp/webhook

Receives WhatsApp messages from Twilio and triggers resume generation workflow.

**Request Format (Twilio):**
```
Content-Type: application/x-www-form-urlencoded

From=whatsapp:%2B1234567890&Body=Find+SDE+roles+in+NYC&MessageSid=SM123456789
```

**Response:**
```json
{
  "status": "message received"
}
```

**Examples:**

1. **Search Query:**
   ```
   From: whatsapp:+1234567890
   Body: Find me backend engineer roles in San Francisco with Python
   ```
   - Triggers Job Search → Curation → Generation → Compilation → Notification

2. **Job Link:**
   ```
   From: whatsapp:+1234567890
   Body: https://www.linkedin.com/jobs/123456789/senior-swe-at-google/
   ```
   - Triggers Job Parser instead of Search

---

### Job Link Submission

#### POST /api/job-link

Submit a job link directly for resume generation.

**Request:**
```json
{
  "job_link": "https://linkedin.com/jobs/123456789",
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "status": "queued",
  "message": "Job link received. Resume generation in progress.",
  "job_link": "https://linkedin.com/jobs/123456789"
}
```

**Status Codes:**
- `200` - Successfully queued
- `400` - Invalid job link format
- `422` - Validation error

---

### Scheduled Trigger

#### POST /api/trigger-search

Manually trigger the scheduled job search.

**Request:**
```bash
curl -X POST http://localhost:8000/api/trigger-search
```

**Response:**
```json
{
  "status": "triggered",
  "message": "Scheduled search initiated",
  "query": "Senior Software Engineer roles in tech hubs"
}
```

#### GET /api/trigger-search/status

Get current scheduler status and next scheduled run time.

**Response:**
```json
{
  "scheduler_running": true,
  "next_run": "2024-01-16T12:00:00",
  "scheduled_time": "12:00",
  "scheduled_query": "Senior Software Engineer roles in tech hubs"
}
```

#### POST /api/trigger-search/update-query

Update the hardcoded query for scheduled searches.

**Request:**
```json
{
  "query": "DevOps Engineer roles with Kubernetes experience"
}
```

**Response:**
```json
{
  "status": "updated",
  "message": "Scheduled query updated",
  "new_query": "DevOps Engineer roles with Kubernetes experience"
}
```

#### POST /api/trigger-search/update-time

Update the scheduled search time.

**Request:**
```json
{
  "time": "14:30"
}
```

**Response:**
```json
{
  "status": "updated",
  "message": "Scheduled time updated",
  "new_time": "14:30"
}
```

---

### Status and Tracking

#### GET /api/status/{job_id}

Get status of a specific job processing.

**Response:**
```json
{
  "job_id": "job_001",
  "status": "completed",
  "resume_pdf": "/output/resume_user_123_job_001.pdf",
  "cover_letter_pdf": "/output/cover_letter_user_123_job_001.pdf",
  "whatsapp_sent": true,
  "generated_at": "2024-01-15T10:00:00Z"
}
```

#### GET /api/resumes

List generated resumes for a user.

**Query Parameters:**
- `user_id` (required) - User ID
- `limit` (optional) - Max results (default: 10)

**Response:**
```json
{
  "user_id": "user_123",
  "total_resumes": 5,
  "resumes": [
    {
      "id": "resume_001",
      "job_title": "Senior Backend Engineer",
      "company": "Google",
      "generated_at": "2024-01-15T10:00:00Z",
      "pdf_path": "/output/resume_1.pdf"
    }
  ]
}
```

#### GET /api/applications

List all applications and generated resumes.

**Query Parameters:**
- `user_id` (required) - User ID
- `status` (optional) - Filter by status (generated, sent, applied, rejected, accepted)

**Response:**
```json
{
  "user_id": "user_123",
  "total_applications": 15,
  "applications": [
    {
      "id": "app_001",
      "job_id": "job_001",
      "job_title": "Senior SDE",
      "company": "Meta",
      "status": "sent",
      "fit_score": 92,
      "created_at": "2024-01-15T09:00:00Z",
      "sent_at": "2024-01-15T10:00:00Z"
    }
  ],
  "status_breakdown": {
    "generated": 8,
    "sent": 5,
    "applied": 2,
    "rejected": 0,
    "accepted": 0
  }
}
```

---

### Health & Config

#### GET /api/health

Check application health.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "api": "ok",
    "database": "ok",
    "ollama_llm": "ok",
    "whatsapp": "ok"
  }
}
```

#### GET /api/config

Get current application configuration (non-sensitive values).

**Response:**
```json
{
  "app_name": "Job Autopilot",
  "app_version": "1.0.0",
  "debug": false,
  "llm_model": "gemma2",
  "scheduled_search_time": "12:00",
  "scheduled_search_query": "Senior Software Engineer roles in tech hubs",
  "features": {
    "mem0_enabled": true,
    "langsmith_enabled": true,
    "mock_mcp_tools": true
  }
}
```

#### GET /api/stats

Get application statistics.

**Response:**
```json
{
  "total_resumes_generated": 42,
  "total_jobs_searched": 150,
  "average_compilation_time_ms": 2500,
  "failed_compilations": 2,
  "successful_whatsapp_sends": 35,
  "avg_fit_score": 82.5
}
```

---

### Error Handling

#### GET /api/errors

Get recent errors and failed jobs (admin endpoint).

**Query Parameters:**
- `limit` (optional) - Max errors to return (default: 50)

**Response:**
```json
{
  "total_errors": 5,
  "errors": [
    {
      "id": "err_001",
      "job_id": "job_001",
      "user_id": "user_123",
      "error_type": "compilation",
      "error_message": "LaTeX compilation failed after 3 attempts",
      "retry_count": 0,
      "failed_at": "2024-01-15T10:00:00Z"
    }
  ],
  "error_types": {
    "compilation": 2,
    "llm": 1,
    "search": 1,
    "notification": 1
  }
}
```

#### POST /api/errors/{error_id}/retry

Retry a failed job.

**Response:**
```json
{
  "status": "retry_queued",
  "error_id": "err_001",
  "message": "Failed job has been re-queued for processing"
}
```

---

## Workflow Examples

### Example 1: WhatsApp Query

```bash
# User sends WhatsApp message: "Find Python SDE roles in SF"
# Twilio forwards to webhook
# System:
# 1. Search: Brave Search for "Python SDE roles in SF"
# 2. Curation: Analyze 10-15 results, rank by fit
# 3. Generation: LLM generates resume tailored to top match
# 4. Compilation: pdflatex compiles resume + cover letter
# 5. Notification: Send PDFs + job link to WhatsApp

POST /api/whatsapp/webhook
From=whatsapp:%2B1234567890&Body=Find+Python+SDE+roles+in+SF&MessageSid=SM123

# Response in 2-3 minutes:
# WhatsApp message:
#   📋 New Job Match!
#   🏢 Google
#   💼 Senior Backend Engineer
#   📍 San Francisco, CA
#   💰 $250k - $350k
#   ✨ Fit Score: 95%
#   🔗 Link: [job link]
#   [resume PDF attachment]
#   [cover letter PDF attachment]
```

### Example 2: Direct Job Link

```bash
curl -X POST http://localhost:8000/api/job-link \
  -H "Content-Type: application/json" \
  -d '{
    "job_link": "https://linkedin.com/jobs/123456789",
    "user_id": "user_123"
  }'

# Response: 
# {
#   "status": "queued",
#   "message": "Job link received. Resume generation in progress.",
#   "job_link": "https://linkedin.com/jobs/123456789"
# }

# In background: Parse job link → Generate resume → Send WhatsApp
```

### Example 3: Scheduled Daily Search

```bash
# Daily at 12:00 PM:
# System runs hardcoded query: "Senior Software Engineer roles in tech hubs"
# Results aggregated and sent to user via WhatsApp

# Manually trigger:
curl -X POST http://localhost:8000/api/trigger-search

# Update scheduled time:
curl -X POST http://localhost:8000/api/trigger-search/update-time \
  -H "Content-Type: application/json" \
  -d '{"time": "14:00"}'
```

---

## Error Responses

All errors return JSON with appropriate HTTP status codes:

```json
{
  "status": "error",
  "message": "Error message",
  "detail": "Detailed error information"
}
```

**Common Status Codes:**
- `200` - Success
- `202` - Accepted (async processing)
- `400` - Bad request
- `404` - Not found
- `422` - Validation error
- `500` - Internal server error

---

## Rate Limiting

Currently no rate limiting implemented. Production deployment should include:
- Per-user rate limits (e.g., 10 searches/hour)
- IP-based rate limiting
- Concurrent request limits

---

## Authentication

Currently no authentication implemented. Production deployment should include:
- JWT token authentication
- API key authentication
- WhatsApp webhook signature verification

---

## Pagination

For list endpoints:

**Query Parameters:**
- `page` (optional) - Page number (default: 1)
- `limit` (optional) - Items per page (default: 10, max: 100)

**Response:**
```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 42,
    "total_pages": 5,
    "has_next": true
  }
}
```
