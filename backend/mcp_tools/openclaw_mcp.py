"""
OpenClaw MCP Tool for job search
OpenClaw is an open-source job board API providing programmatic access to job listings
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from models.core import JobPosting
from config.settings import settings
from core.logger import get_logger

logger = get_logger("job_autopilot.mcp.openclaw")


class OpenClawMCPTool:
    """
    MCP Tool wrapper for OpenClaw API
    OpenClaw provides open-source access to job board data
    Supports both real API calls and mock implementation
    
    API Documentation: https://openclaw.dev/docs
    Authentication: API Key-based via header
    Rate Limit: Varies by plan (typically 100-1000 req/hour)
    """
    
    def __init__(self, use_mock: bool = False):
        """
        Initialize OpenClaw MCP Tool
        
        Args:
            use_mock: Use mock data for testing (default: False if real API key provided)
        """
        self.use_mock = use_mock or settings.USE_MOCK_MCP_TOOLS
        self.api_key = settings.OPENCLAW_API_KEY
        self.base_url = settings.OPENCLAW_BASE_URL
        self.request_timeout = 30
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        
        logger.info(
            "OpenClaw MCP Tool initialized",
            extra={
                "use_mock": self.use_mock,
                "base_url": self.base_url,
                "has_api_key": bool(self.api_key and self.api_key != "openclaw_test_key_12345")
            }
        )
    
    async def search(
        self,
        query: str,
        count: int = 10,
        offset: int = 0,
        filters: Optional[Dict] = None
    ) -> List[JobPosting]:
        """
        Search for job postings via OpenClaw
        
        Args:
            query: Search query (e.g., "Python SDE roles in San Francisco")
            count: Number of results to return (max 100)
            offset: Pagination offset
            filters: Optional filters (location, salary_min, salary_max, company, etc.)
        
        Returns:
            List of JobPosting objects
            
        Raises:
            Exception: If search fails after retries
        """
        logger.info(
            "OpenClaw search invoked",
            extra={
                "query": query,
                "count": count,
                "offset": offset,
                "use_mock": self.use_mock,
                "has_filters": filters is not None
            }
        )
        
        # Validate and normalize count
        count = min(count, 100)  # OpenClaw API max is typically 100
        
        try:
            if self.use_mock:
                return await self._mock_search(query, count, filters)
            else:
                return await self._real_search(query, count, offset, filters)
        
        except Exception as e:
            logger.error(
                "OpenClaw search failed",
                extra={
                    "query": query,
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                exc_info=True
            )
            raise
    
    async def _real_search(
        self,
        query: str,
        count: int,
        offset: int,
        filters: Optional[Dict] = None
    ) -> List[JobPosting]:
        """
        Execute real API call to OpenClaw
        
        Note: This is a placeholder. Implementation requires:
        - aiohttp or httpx for async HTTP
        - OpenClaw API credentials
        - Proper error handling and retry logic
        """
        try:
            import aiohttp
        except ImportError:
            logger.warning("aiohttp not available, using mock results")
            return await self._mock_search(query, count, filters)
        
        logger.info(
            "Executing real OpenClaw API search",
            extra={"query": query, "count": count}
        )
        
        # Prepare request parameters
        params = {
            "q": query,
            "limit": count,
            "offset": offset,
        }
        
        # Add filters if provided
        if filters:
            if "location" in filters:
                params["location"] = filters["location"]
            if "salary_min" in filters:
                params["salary_min"] = filters["salary_min"]
            if "salary_max" in filters:
                params["salary_max"] = filters["salary_max"]
            if "company" in filters:
                params["company"] = filters["company"]
            if "job_type" in filters:
                params["job_type"] = filters["job_type"]
        
        headers = {
            "Authorization": f"******",
            "Content-Type": "application/json",
        }
        
        # Retry logic
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}/jobs/search",
                        params=params,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=self.request_timeout)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            jobs = data.get("jobs", [])
                            
                            logger.info(
                                "OpenClaw API search successful",
                                extra={
                                    "query": query,
                                    "results_count": len(jobs),
                                    "total_results": data.get("total", 0)
                                }
                            )
                            
                            return self._parse_openclaw_jobs(jobs)
                        
                        elif response.status == 401:
                            logger.error(
                                "OpenClaw authentication failed",
                                extra={"status": response.status}
                            )
                            raise ValueError("Invalid OpenClaw API key")
                        
                        elif response.status == 429:
                            # Rate limit hit
                            if attempt < self.max_retries - 1:
                                wait_time = self.retry_delay * (2 ** attempt)
                                logger.warning(
                                    "OpenClaw rate limited, retrying",
                                    extra={
                                        "attempt": attempt + 1,
                                        "wait_seconds": wait_time
                                    }
                                )
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                raise Exception("OpenClaw rate limit exceeded after retries")
                        
                        else:
                            logger.error(
                                "OpenClaw API error",
                                extra={
                                    "status": response.status,
                                    "body": await response.text()
                                }
                            )
                            raise Exception(f"OpenClaw API error: {response.status}")
            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning(
                    "OpenClaw network error, retrying",
                    extra={
                        "attempt": attempt + 1,
                        "error": str(e)
                    }
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    raise
        
        # Fallback to mock if real API fails completely
        logger.warning("OpenClaw API exhausted retries, falling back to mock")
        return await self._mock_search(query, count, filters)
    
    async def _mock_search(
        self,
        query: str,
        count: int = 10,
        filters: Optional[Dict] = None
    ) -> List[JobPosting]:
        """
        Mock job search for testing without real API
        Simulates realistic OpenClaw job posting responses
        """
        logger.debug(
            "Using mock OpenClaw search results",
            extra={"query": query, "count": count, "filters": filters}
        )
        
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        mock_jobs = [
            JobPosting(
                id=f"openclaw_{i:04d}",
                title=self._get_title_for_query(query, i),
                company=self._get_company(i),
                description=self._get_description(query, i),
                location=self._get_location(i, filters),
                salary_range=self._get_salary_range(i),
                job_link=f"https://openclaw.dev/jobs/{i:04d}",
                posted_date=datetime.now() - timedelta(days=i % 30),
                source="openclaw"
            )
            for i in range(count)
        ]
        
        logger.info(
            "Mock OpenClaw search completed",
            extra={
                "query": query,
                "results_count": len(mock_jobs),
                "filters_applied": filters is not None
            }
        )
        
        return mock_jobs
    
    def _parse_openclaw_jobs(self, jobs: List[Dict]) -> List[JobPosting]:
        """
        Parse raw OpenClaw API response into JobPosting models
        
        Expected OpenClaw response format:
        {
            "id": "job_123",
            "title": "Senior Software Engineer",
            "company_name": "Company",
            "description": "Job description...",
            "location": "City, State",
            "salary_min": 150000,
            "salary_max": 250000,
            "currency": "USD",
            "job_url": "https://...",
            "posted_at": "2024-01-15T10:00:00Z",
            "job_type": "full_time"
        }
        """
        parsed_jobs = []
        
        for job in jobs:
            try:
                # Handle salary range
                salary_range = None
                if job.get("salary_min") or job.get("salary_max"):
                    salary_min = job.get("salary_min", 0)
                    salary_max = job.get("salary_max", 0)
                    currency = job.get("currency", "USD")
                    if salary_min and salary_max:
                        salary_range = f"{currency} {salary_min:,} - {salary_max:,}"
                    elif salary_min:
                        salary_range = f"{currency} {salary_min:,}+"
                    elif salary_max:
                        salary_range = f"{currency} up to {salary_max:,}"
                
                # Parse posted date
                posted_date = datetime.now()
                if job.get("posted_at"):
                    try:
                        # Assume ISO 8601 format from OpenClaw
                        posted_date = datetime.fromisoformat(
                            job["posted_at"].replace("Z", "+00:00")
                        )
                    except (ValueError, AttributeError):
                        logger.warning(
                            "Failed to parse job posted_at",
                            extra={"posted_at": job.get("posted_at")}
                        )
                
                job_posting = JobPosting(
                    id=job.get("id", f"openclaw_{hash(job)}"),
                    title=job.get("title", "Unknown Position"),
                    company=job.get("company_name", "Unknown Company"),
                    description=job.get("description", ""),
                    location=job.get("location", "Remote"),
                    salary_range=salary_range,
                    job_link=job.get("job_url", job.get("url", "")),
                    posted_date=posted_date,
                    source="openclaw"
                )
                
                parsed_jobs.append(job_posting)
                
            except Exception as e:
                logger.warning(
                    "Failed to parse OpenClaw job",
                    extra={
                        "job_id": job.get("id", "unknown"),
                        "error": str(e)
                    }
                )
                continue
        
        logger.info(
            "OpenClaw jobs parsed",
            extra={
                "total_received": len(jobs),
                "successfully_parsed": len(parsed_jobs)
            }
        )
        
        return parsed_jobs
    
    @staticmethod
    def _get_title_for_query(query: str, index: int) -> str:
        """Generate realistic title based on query"""
        if "sde" in query.lower() or "software" in query.lower():
            titles = [
                "Senior Software Engineer",
                "Software Engineer - Backend",
                "Full Stack Engineer",
                "Software Engineer - Infrastructure",
                "Senior Backend Engineer",
                "Platform Engineer",
                "Systems Engineer",
                "Software Architect",
                "Lead Engineer - Backend",
                "Software Engineer III"
            ]
            return titles[index % len(titles)]
        
        if "devops" in query.lower():
            titles = [
                "DevOps Engineer",
                "Senior DevOps Engineer",
                "Infrastructure Engineer",
                "Platform Engineer",
                "SRE Engineer",
                "Cloud Engineer",
                "Operations Engineer",
            ]
            return titles[index % len(titles)]
        
        if "ml" in query.lower() or "machine" in query.lower() or "ai" in query.lower():
            titles = [
                "Machine Learning Engineer",
                "Senior ML Engineer",
                "ML Ops Engineer",
                "Data Scientist",
                "AI Engineer",
                "ML Research Engineer",
                "Applied ML Engineer",
            ]
            return titles[index % len(titles)]
        
        if "data" in query.lower():
            titles = [
                "Data Engineer",
                "Senior Data Engineer",
                "Data Scientist",
                "Analytics Engineer",
                "Data Platform Engineer",
            ]
            return titles[index % len(titles)]
        
        return f"Software Engineer {index + 1}"
    
    @staticmethod
    def _get_company(index: int) -> str:
        """Get realistic company name"""
        companies = [
            "Google",
            "Meta",
            "Amazon",
            "Microsoft",
            "Apple",
            "OpenAI",
            "Anthropic",
            "Stripe",
            "Figma",
            "Notion",
            "Slack",
            "Airbnb",
            "Netflix",
            "Tesla",
            "Uber",
            "Lyft",
            "Twitch",
            "Discord",
            "GitHub",
            "GitLab",
        ]
        return companies[index % len(companies)]
    
    @staticmethod
    def _get_location(index: int, filters: Optional[Dict] = None) -> str:
        """Get realistic location (respecting filters if provided)"""
        if filters and "location" in filters:
            return filters["location"]
        
        locations = [
            "San Francisco, CA",
            "New York, NY",
            "Seattle, WA",
            "Austin, TX",
            "Denver, CO",
            "Los Angeles, CA",
            "Mountain View, CA",
            "Redmond, WA",
            "Cupertino, CA",
            "Remote",
            "London, UK",
            "Toronto, Canada",
            "Singapore",
            "Berlin, Germany",
            "Tokyo, Japan",
        ]
        return locations[index % len(locations)]
    
    @staticmethod
    def _get_salary_range(index: int) -> str:
        """Get realistic salary range"""
        base_salary = 150000 + (index * 15000)
        max_salary = base_salary + 100000
        return f"USD ${base_salary:,} - ${max_salary:,}"
    
    @staticmethod
    def _get_description(query: str, index: int) -> str:
        """Get realistic job description"""
        if "senior" in query.lower():
            seniority = "5+ years"
        elif "junior" in query.lower():
            seniority = "0-2 years"
        else:
            seniority = "3+ years"
        
        description = f"""
We're looking for a talented engineer to join our team.

Requirements:
- {seniority} of professional software development experience
- Strong programming skills (Python, Go, Rust, or similar)
- Experience with distributed systems and cloud infrastructure
- Bachelor's degree in Computer Science or equivalent experience
- Excellent problem-solving and communication skills

Responsibilities:
- Design and implement scalable systems
- Collaborate with cross-functional teams
- Participate in code reviews and technical discussions
- Contribute to technical documentation and knowledge sharing
- Mentor junior engineers and support team growth

Benefits:
- Competitive salary and equity
- Comprehensive health insurance
- Unlimited PTO and flexible work arrangements
- Remote work options
- Professional development budget
- Collaborative and innovative team environment
"""
        return description


# Singleton instance
_openclaw_tool = None


def get_openclaw_tool() -> OpenClawMCPTool:
    """Get OpenClaw MCP tool instance"""
    global _openclaw_tool
    if _openclaw_tool is None:
        _openclaw_tool = OpenClawMCPTool()
    return _openclaw_tool
