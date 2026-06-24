"""
Job Search Agent - First step in the pipeline
Searches for job postings using Brave Search
"""

from typing import List
from models.core import JobPosting, JobSearchRequest, AgentState
from mcp_tools.brave_search_mcp import get_brave_search_tool
from core.logger import get_logger

logger = get_logger("job_autopilot.agents.search_agent")


class JobSearchAgent:
    """
    Responsible for searching job postings based on user query
    Uses Brave Search MCP tool
    """
    
    def __init__(self, max_results: int = 15):
        self.max_results = max_results
        self.search_tool = get_brave_search_tool()
    
    async def invoke(self, state: AgentState) -> AgentState:
        """
        Execute job search
        
        Args:
            state: Current agent state with job_search_request
        
        Returns:
            Updated state with job_postings
        """
        request = state.job_search_request
        
        logger.info(
            "Job Search Agent invoked",
            extra={
                "query": request.query,
                "user_id": request.user_id,
                "input_source": request.input_source
            }
        )
        
        try:
            # Execute search
            job_postings = await self.search_tool.search(
                query=request.query,
                count=self.max_results
            )
            
            logger.info(
                "Job search completed",
                extra={
                    "query": request.query,
                    "results_count": len(job_postings)
                }
            )
            
            # Update state
            state.job_postings = job_postings
            
            if not job_postings:
                logger.warning(
                    "No jobs found for query",
                    extra={"query": request.query}
                )
                state.errors.append(f"No jobs found for query: {request.query}")
            
            return state
        
        except Exception as e:
            logger.error(
                "Job search failed",
                extra={
                    "query": request.query,
                    "error": str(e)
                },
                exc_info=True
            )
            state.errors.append(f"Job search error: {str(e)}")
            return state


def create_job_search_agent(max_results: int = 15) -> JobSearchAgent:
    """Factory function to create Job Search Agent"""
    return JobSearchAgent(max_results=max_results)
