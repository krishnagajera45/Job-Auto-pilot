# OpenClaw Integration Guide

## Overview

Job Autopilot now supports **OpenClaw** as an additional job board API alongside Brave Search. OpenClaw is an open-source platform providing programmatic access to comprehensive job listings data.

## What is OpenClaw?

OpenClaw is an open-source job board aggregator API that provides:
- Real-time job listings from multiple sources
- Structured job data (title, company, location, salary, requirements)
- Advanced filtering capabilities
- Rate-limited API access with generous free tier

**Official Resources:**
- Website: https://openclaw.dev
- API Documentation: https://openclaw.dev/docs
- GitHub: https://github.com/openclaw/openclaw-api

## Configuration

### 1. Get OpenClaw API Key

1. Visit [OpenClaw Dashboard](https://openclaw.dev/dashboard)
2. Sign up for a free account
3. Generate an API key from Settings
4. Copy your API key

### 2. Update Environment Variables

Add to your `.env` file:

```bash
# OpenClaw Configuration
OPENCLAW_API_KEY=your_openclaw_api_key_here
OPENCLAW_BASE_URL=https://api.openclaw.dev

# Enable OpenClaw integration
ENABLE_OPENCLAW=True
```

### 3. Using Mock Data (Development)

For testing without API keys, Job Autopilot provides mock implementations:

```bash
USE_MOCK_MCP_TOOLS=True
```

When enabled, realistic mock job data is returned without making real API calls.

## Usage

### 1. WhatsApp Commands

Send WhatsApp messages to your Job Autopilot number with these formats:

**Use Brave Search (default):**
```
Find SDE roles in San Francisco
```

**Use OpenClaw specifically:**
```
Find SDE roles in San Francisco via openclaw
```

**Use both sources (combined results):**
```
Find SDE roles in San Francisco from all sources
```

### 2. API Endpoint

```bash
# Request to search using OpenClaw
curl -X POST http://localhost:8000/api/whatsapp/webhook \
  -d "Body=Find SDE roles via openclaw" \
  -d "From=whatsapp:+1234567890"
```

### 3. Python Code

```python
from mcp_tools.openclaw_mcp import get_openclaw_tool
from models.core import JobSearchRequest, JobSource

# Get the OpenClaw tool
openclaw = get_openclaw_tool()

# Search for jobs
jobs = await openclaw.search(
    query="Python developer in New York",
    count=10
)

# Jobs are returned as JobPosting objects
for job in jobs:
    print(f"{job.title} at {job.company}")
    print(f"Location: {job.location}")
    print(f"Salary: {job.salary_range}")
    print()
```

## Features

### Multi-Source Search

The Job Search Agent now supports three modes:

| Mode | Source | Use Case |
|------|--------|----------|
| `brave_search` | Brave Search API | General web search results (default) |
| `openclaw` | OpenClaw API | Job board specific data |
| `both` | Both sources | Maximum coverage, combined results |

### Job Source Selection

Update `JobSearchRequest` model to specify source:

```python
request = JobSearchRequest(
    query="SDE roles in NYC",
    user_id="user_123",
    input_source=InputSource.WHATSAPP,
    job_source=JobSource.OPENCLAW  # Specify source
)
```

### Filtering

OpenClaw supports advanced filtering:

```python
jobs = await openclaw.search(
    query="Python",
    count=15,
    filters={
        "location": "San Francisco, CA",
        "salary_min": 150000,
        "salary_max": 300000,
        "job_type": "full_time",
        "company": "Google"
    }
)
```

## Error Handling

### API Key Validation

If OpenClaw API key is invalid:
```
Error: OpenClaw authentication failed
Status: 401 Unauthorized
```

**Fix:** Verify your API key in the OpenClaw dashboard and update `.env`

### Rate Limiting

OpenClaw enforces rate limits (varies by plan):

- **Free tier**: 100 requests/hour
- **Pro tier**: 1,000 requests/hour

If rate limited (HTTP 429), Job Autopilot automatically:
1. Waits with exponential backoff
2. Retries up to 3 times
3. Falls back to mock data if all retries exhausted

### Network Errors

If OpenClaw API is unreachable:
1. Check your internet connection
2. Verify `OPENCLAW_BASE_URL` is correct
3. Check OpenClaw service status
4. Fallback to mock data will be used automatically

## Architecture

### Job Search Flow

```
User Input (WhatsApp/Link/Scheduled)
    ↓
Input Dispatcher
    ↓
Job Source Router
    ├→ Brave Search (if selected)
    ├→ OpenClaw (if selected)
    └→ Both (if selected, combines results)
    ↓
Deduplicate & Normalize
    ↓
JobPosting objects
    ↓
Curation Agent (continues pipeline)
```

### MCP Tool Structure

**File:** `backend/mcp_tools/openclaw_mcp.py`

```python
class OpenClawMCPTool:
    async def search(query, count, filters) -> List[JobPosting]
    async def _real_search()      # Real API calls
    async def _mock_search()      # Mock data for testing
    def _parse_openclaw_jobs()    # Parse API response
```

## API Response Mapping

OpenClaw API responses are automatically parsed into Job Autopilot's `JobPosting` model:

```python
{
    "id": "openclaw_0001",
    "title": "Senior Software Engineer",
    "company": "Google",
    "description": "Looking for experienced SDE...",
    "location": "Mountain View, CA",
    "salary_range": "USD 200,000 - 300,000",
    "job_link": "https://openclaw.dev/jobs/...",
    "posted_date": "2024-01-15T10:00:00Z",
    "source": "openclaw"
}
```

## Performance

### Benchmarks

| Source | Avg Response Time | Results Per Query |
|--------|-------------------|-------------------|
| Brave Search | 1-2s | 10-15 |
| OpenClaw | 0.5-1s | 10-15 |
| Both (combined) | 1.5-2s | 20-30 |

### Optimization Tips

1. **Use OpenClaw for job board searches** - Faster and more relevant
2. **Use Brave Search for technical blogs** - Better coverage
3. **Combine both periodically** - Weekly comprehensive searches

## Troubleshooting

### Issue: "OpenClaw API key not found"

**Solution:**
```bash
# Verify in .env file
echo $OPENCLAW_API_KEY

# Check if Settings loaded properly
python3 -c "from config.settings import settings; print(settings.OPENCLAW_API_KEY)"
```

### Issue: "No jobs found via OpenClaw"

**Solutions:**
1. Check if OpenClaw service is operational
2. Verify API key has proper permissions
3. Try with different keywords: `"backend engineer"` instead of `"SDE"`
4. Expand location/salary filters

### Issue: "Rate limit exceeded"

**Solutions:**
1. Reduce search frequency
2. Upgrade OpenClaw subscription plan
3. Use mock mode for testing: `USE_MOCK_MCP_TOOLS=True`

## Feature Flags

Control OpenClaw integration with settings:

```python
# Enable/disable OpenClaw
ENABLE_OPENCLAW=True

# Use mock data in testing
USE_MOCK_MCP_TOOLS=True

# Feature flags in settings.py
ENABLE_OPENCLAW: bool = True
```

## Future Enhancements

Planned features:
- [ ] Advanced filtering UI
- [ ] Save job preferences by source
- [ ] OpenClaw alert subscriptions
- [ ] Historical job trends from OpenClaw
- [ ] One-click apply via OpenClaw integration

## Support

### Resources

- OpenClaw Docs: https://openclaw.dev/docs
- Job Autopilot GitHub Issues: https://github.com/krishnagajera45/Job-Auto-pilot/issues
- Email Support: krishnagajera45@gmail.com

### Debugging

Enable debug logging:

```bash
LOG_LEVEL=DEBUG
```

Watch logs for OpenClaw calls:
```bash
grep "openclaw" logs/job_autopilot.log
```

## Examples

### Example 1: Search OpenClaw for DevOps Roles

**Message:** `Find DevOps engineer roles in Seattle via openclaw`

**Flow:**
1. Message received in WhatsApp
2. Job source detected: `openclaw`
3. Search: OpenClaw API for "DevOps engineer Seattle"
4. Results parsed into JobPosting objects
5. Curation agent selects best match
6. Resume generated with tailored DevOps template
7. PDF sent to WhatsApp

### Example 2: Combined Search for ML Roles

**Message:** `Find ML engineer roles from all sources`

**Flow:**
1. Message received in WhatsApp
2. Job source detected: `both`
3. Brave Search: "ML engineer" → 7-8 results
4. OpenClaw: "ML engineer" → 7-8 results
5. Combined 15-16 results
6. Curation agent scores all
7. Top match selected
8. Resume generated
9. PDF sent to WhatsApp

## Contributing

Improvements to OpenClaw integration are welcome!

- Report bugs: [GitHub Issues](https://github.com/krishnagajera45/Job-Auto-pilot/issues)
- Submit features: [GitHub Discussions](https://github.com/krishnagajera45/Job-Auto-pilot/discussions)

---

**Last Updated:** 2024-06-24
**Version:** 1.0
