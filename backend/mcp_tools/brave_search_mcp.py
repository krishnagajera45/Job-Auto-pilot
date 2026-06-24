"""
Brave Search MCP Tool for job search
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from models.core import JobPosting
from config.settings import settings
from core.logger import get_logger

logger = get_logger("job_autopilot.mcp.brave_search")


class BraveSearchMCPTool:
    """
    MCP Tool wrapper for Brave Search API
    Supports both real API calls and mock implementation
    """
    
    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock or settings.USE_MOCK_MCP_TOOLS
        self.api_key = settings.BRAVE_SEARCH_API_KEY
    
    async def search(
        self,
        query: str,
        count: int = 10,
        offset: int = 0
    ) -> List[JobPosting]:
        """
        Search for job postings
        
        Args:
            query: Search query (e.g., "Python SDE roles in San Francisco")
            count: Number of results to return
            offset: Pagination offset
        
        Returns:
            List of JobPosting objects
        """
        logger.info(
            "Executing job search",
            extra={
                "query": query,
                "count": count,
                "use_mock": self.use_mock
            }
        )
        
        try:
            if self.use_mock:
                return await self._mock_search(query, count)
            else:
                return await self._real_search(query, count, offset)
        
        except Exception as e:
            logger.error(
                "Search failed",
                extra={"query": query, "error": str(e)},
                exc_info=True
            )
            raise
    
    async def _real_search(
        self,
        query: str,
        count: int,
        offset: int
    ) -> List[JobPosting]:
        """
        Real API call to Brave Search
        (Placeholder - implement with actual API)
        """
        # TODO: Implement real Brave Search API call
        # For now, return mock results
        logger.warning("Real Brave Search API not yet implemented, using mock")
        return await self._mock_search(query, count)
    
    async def _mock_search(
        self,
        query: str,
        count: int = 10
    ) -> List[JobPosting]:
        """
        Mock job search for testing
        Simulates realistic job posting results
        """
        logger.debug(
            "Using mock search results",
            extra={"query": query, "count": count}
        )
        
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        mock_jobs = [
            JobPosting(
                id=f"job_{i:03d}",
                title=self._get_title_for_query(query, i),
                company=self._get_company(i),
                description=self._get_description(query, i),
                location=self._get_location(i),
                salary_range=f"${150 + i*10}k - ${220 + i*15}k",
                job_link=f"https://example.com/job/{i}",
                posted_date=datetime.now(),
                source="brave_search"
            )
            for i in range(count)
        ]
        
        logger.info(
            "Mock search completed",
            extra={
                "query": query,
                "results_count": len(mock_jobs)
            }
        )
        
        return mock_jobs
    
    @staticmethod
    def _get_title_for_query(query: str, index: int) -> str:
        """Generate title based on query"""
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
            ]
            return titles[index % len(titles)]
        
        if "ml" in query.lower() or "machine" in query.lower():
            titles = [
                "Machine Learning Engineer",
                "Senior ML Engineer",
                "ML Ops Engineer",
                "Data Scientist",
                "AI Engineer",
            ]
            return titles[index % len(titles)]
        
        return f"Software Engineer {index + 1}"
    
    @staticmethod
    def _get_company(index: int) -> str:
        """Get company name"""
        companies = [
            "Google",
            "Meta",
            "Amazon",
            "Microsoft",
            "Apple",
            "OpenAI",
            "Stripe",
            "Figma",
            "Notion",
            "Slack",
            "Airbnb",
            "Netflix",
            "Tesla",
            "Uber",
            "Lyft"
        ]
        return companies[index % len(companies)]
    
    @staticmethod
    def _get_location(index: int) -> str:
        """Get location"""
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
        ]
        return locations[index % len(locations)]
    
    @staticmethod
    def _get_description(query: str, index: int) -> str:
        """Get job description"""
        if "senior" in query.lower():
            seniority = "5+ years"
        elif "junior" in query.lower():
            seniority = "0-2 years"
        else:
            seniority = "3+ years"
        
        description = f"""
We're looking for a talented engineer to join our team.

Requirements:
- {seniority} of software development experience
- Strong programming skills (Python, Go, or similar)
- Experience with distributed systems and cloud infrastructure
- Bachelor's degree in Computer Science or equivalent
- Excellent problem-solving skills

Responsibilities:
- Design and implement scalable systems
- Collaborate with cross-functional teams
- Participate in code reviews
- Contribute to technical documentation
- Mentor junior engineers

Benefits:
- Competitive salary
- Stock options
- Health insurance
- Remote work option
- Professional development budget
"""
        return description


# Singleton instance
_brave_search_tool = None


def get_brave_search_tool() -> BraveSearchMCPTool:
    """Get Brave Search MCP tool instance"""
    global _brave_search_tool
    if _brave_search_tool is None:
        _brave_search_tool = BraveSearchMCPTool()
    return _brave_search_tool
