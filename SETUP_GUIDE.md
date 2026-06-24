# Job Autopilot - Setup & Installation Guide

## Table of Contents
1. [Quick Start (Docker)](#quick-start-docker)
2. [Local Development Setup](#local-development-setup)
3. [Configuration](#configuration)
4. [Running the System](#running-the-system)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start (Docker)

### Prerequisites
- Docker and Docker Compose installed
- 8GB+ RAM available
- 10GB+ disk space (for Ollama model)

### Steps

1. **Clone repository:**
   ```bash
   git clone https://github.com/krishnagajera45/Job-Auto-pilot.git
   cd Job-Auto-pilot
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start services:**
   ```bash
   docker-compose up -d
   ```
   
   This starts:
   - Ollama (LLM service on port 11434)
   - FastAPI backend (on port 8000)
   - SQLite database

4. **Wait for Ollama to initialize:**
   ```bash
   # Watch logs
   docker-compose logs -f ollama
   
   # Wait until you see "Listening on [::]:11434"
   # Then Ctrl+C to exit
   ```

5. **Download Ollama model:**
   ```bash
   docker exec job-autopilot-ollama ollama pull gemma2
   # This downloads ~3GB model (takes 5-10 minutes)
   ```

6. **Verify setup:**
   ```bash
   # Check API health
   curl http://localhost:8000/api/health
   
   # Should return:
   # {"status": "healthy", "services": {...}}
   ```

7. **Access API documentation:**
   Open browser: `http://localhost:8000/docs`

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- Ollama installed locally
- TeX Live (for LaTeX compilation)
- Git

### macOS

```bash
# Install Ollama
brew install ollama

# Start Ollama in background
ollama serve &

# Download model
ollama pull gemma2

# Install TeX Live
brew install texlive

# Or minimal installation:
brew install --cask mactex-no-gui
```

### Ubuntu/Debian

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve &

# Download model
ollama pull gemma2

# Install TeX Live
sudo apt-get install -y texlive-latex-base texlive-latex-extra texlive-fonts-recommended
```

### Windows

```bash
# Install Ollama
# Download from https://ollama.ai/download

# Install TeX Live
# Download from https://tug.org/texlive/windows.html
# Or use MiKTeX: https://miktex.org/download

# Install Python 3.11+
# Download from https://www.python.org/downloads/
```

### Setup Python Environment

```bash
# Clone repository
git clone https://github.com/krishnagajera45/Job-Auto-pilot.git
cd Job-Auto-pilot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Copy environment file
cp ../.env.example ../.env
# Edit ../.env with your settings
```

### Run Application

```bash
# Terminal 1: Start Ollama (if not already running)
ollama serve

# Terminal 2: Start FastAPI server
cd backend
python main.py

# Terminal 3: Access API
# Open browser to http://localhost:8000/docs
# Or test with curl:
curl http://localhost:8000/api/health
```

---

## Configuration

### .env File

Copy `.env.example` to `.env` and fill in required values:

```bash
cp .env.example .env
nano .env  # or use your favorite editor
```

### Required Configuration

#### LLM Setup
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma2
```

#### API Keys (Optional for testing)
```env
# For real Brave Search (optional)
BRAVE_SEARCH_API_KEY=your_key_here

# For WhatsApp integration
TWILIO_ACCOUNT_SID=your_sid_here
TWILIO_AUTH_TOKEN=your_token_here
TWILIO_WHATSAPP_NUMBER=+1234567890

# For Mem0 (optional)
MEM0_API_KEY=your_key_here

# For LangSmith tracing (optional)
LANGSMITH_API_KEY=your_key_here
```

#### Scheduling
```env
SCHEDULED_SEARCH_TIME=12:00
SCHEDULED_SEARCH_QUERY=Senior Software Engineer roles in tech hubs
```

#### Feature Flags
```env
# Use mock implementations for testing (no real API calls)
USE_MOCK_MCP_TOOLS=True

# Enable LLM-based error correction
ENABLE_LLM_ERROR_CORRECTION=True

# Enable observability tracing
ENABLE_LANGSMITH=False
```

---

## Running the System

### Test WhatsApp Message

```bash
curl -X POST http://localhost:8000/api/whatsapp/webhook \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:%2B1234567890&Body=Find+SDE+roles+in+NYC&MessageSid=test123"
```

### Test Job Link Submission

```bash
curl -X POST http://localhost:8000/api/job-link \
  -H "Content-Type: application/json" \
  -d '{
    "job_link": "https://www.linkedin.com/jobs/3456789/",
    "user_id": "user_123"
  }'
```

### Trigger Scheduled Search

```bash
curl -X POST http://localhost:8000/api/trigger-search
```

### View Generated Resumes

```bash
ls -la backend/output/
# Generated PDFs will appear here
```

### Monitor Logs

```bash
# Docker
docker-compose logs -f backend

# Local development
# Check job_autopilot.log file created in working directory
tail -f job_autopilot.log
```

---

## Testing

### Run Tests

```bash
cd backend
pytest -v
```

### Test Coverage

```bash
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

### Manual Integration Test

1. **Test Search Agent:**
   ```bash
   python -c "
   import asyncio
   from agents.search_agent import create_job_search_agent
   from models.core import JobSearchRequest, AgentState, InputSource
   
   async def test():
       agent = create_job_search_agent()
       request = JobSearchRequest(
           query='Python SDE roles',
           user_id='test_user',
           input_source=InputSource.WHATSAPP
       )
       state = AgentState(job_search_request=request)
       result = await agent.invoke(state)
       print(f'Found {len(result.job_postings)} jobs')
   
   asyncio.run(test())
   "
   ```

2. **Test LaTeX Compilation:**
   ```bash
   python -c "
   import asyncio
   from mcp_tools.latex_compiler_mcp import get_latex_compiler_tool
   
   async def test():
       compiler = get_latex_compiler_tool()
       latex_code = r'''
       \documentclass{article}
       \begin{document}
       \textbf{Test Resume}
       \end{document}
       '''
       pdf_path = await compiler.compile(latex_code, 'test_resume')
       print(f'PDF created at: {pdf_path}')
   
   asyncio.run(test())
   "
   ```

---

## Troubleshooting

### Issue: Ollama connection refused

**Solution:**
```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it:
ollama serve

# In Docker:
docker-compose logs ollama
docker-compose restart ollama
```

### Issue: Model not found

**Solution:**
```bash
# Pull the model
ollama pull gemma2

# In Docker:
docker exec job-autopilot-ollama ollama pull gemma2
```

### Issue: LaTeX compilation fails

**Solution:**
```bash
# Verify pdflatex is installed
which pdflatex

# If not installed:
# macOS: brew install texlive
# Ubuntu: sudo apt-get install texlive-latex-base
# Windows: Install MiKTeX or TeX Live

# Check logs for detailed error
cat job_autopilot.log | grep "LaTeX"
```

### Issue: Memory errors

**Solution:**
```bash
# Increase Docker memory limit
# Edit docker-compose.yml:
services:
  backend:
    mem_limit: 4g  # Increase as needed
  ollama:
    mem_limit: 4g

# Restart containers
docker-compose down
docker-compose up -d
```

### Issue: Slow PDF generation

**Solution:**
- Increase `mem_limit` for containers
- Use a faster machine (SSD recommended)
- Monitor logs: `docker-compose logs -f backend`

### Issue: WhatsApp messages not being received

**Solution:**
1. Verify Twilio webhook URL is correct:
   ```
   https://your-domain.com/api/whatsapp/webhook
   ```

2. Verify webhook token in environment:
   ```bash
   # Set in Twilio Console
   WHATSAPP_WEBHOOK_TOKEN=your_token
   ```

3. Check logs:
   ```bash
   docker-compose logs -f backend | grep -i whatsapp
   ```

### Issue: Port already in use

**Solution:**
```bash
# Find process using port
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
# In docker-compose.yml, change:
# ports:
#   - "8001:8000"  # Use 8001 instead
```

### Issue: Database errors

**Solution:**
```bash
# Reset database
rm backend/job_autopilot.db

# Recreate tables (happens automatically on startup)
cd backend
python -c "from dependencies import Base, engine; Base.metadata.create_all(bind=engine)"
```

---

## Production Deployment

### Pre-Production Checklist

- [ ] Set `DEBUG=False` in .env
- [ ] Set `USE_MOCK_MCP_TOOLS=False` and configure real APIs
- [ ] Configure PostgreSQL instead of SQLite
- [ ] Set up LangSmith for observability
- [ ] Configure Mem0 for user context
- [ ] Set up authentication (JWT tokens)
- [ ] Configure CORS properly (don't use `*`)
- [ ] Set up HTTPS/SSL
- [ ] Configure monitoring and alerting
- [ ] Set up backup strategy for database
- [ ] Configure rate limiting

### Docker Production Build

```bash
# Build production image
docker build -t job-autopilot:latest \
  -f backend/Dockerfile \
  --build-arg ENVIRONMENT=production \
  .

# Push to registry
docker tag job-autopilot:latest your-registry/job-autopilot:latest
docker push your-registry/job-autopilot:latest

# Run on production
docker run -d \
  --name job-autopilot-prod \
  --env-file .env.prod \
  -p 8000:8000 \
  -v /data/output:/app/output \
  your-registry/job-autopilot:latest
```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests (if available).

---

## Getting Help

- 📖 [Full Documentation](README.md)
- 🏗️ [Architecture Guide](ARCHITECTURE.md)
- 📡 [API Reference](API_REFERENCE.md)
- 🐛 [Report Issues](https://github.com/krishnagajera45/Job-Auto-pilot/issues)
- 💬 [Discord Community](https://discord.gg/job-autopilot)

---

## Next Steps

1. **Configure your preferences:**
   - Update `SCHEDULED_SEARCH_QUERY` to match your job search
   - Add your skills to Mem0 for better curation

2. **Connect WhatsApp:**
   - Set up Twilio account
   - Configure webhook URL
   - Test with sample messages

3. **Customize templates:**
   - Modify LaTeX resume templates in `config/templates/`
   - Add your own template for specific roles

4. **Monitor and iterate:**
   - Check LangSmith traces
   - Collect feedback on generated resumes
   - Refine prompts based on results

---

Happy job hunting! 🚀
