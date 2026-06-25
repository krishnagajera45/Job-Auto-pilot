"""
Job Search Agent - First step in the pipeline
Searches for job postings using multiple sources (Brave Search, OpenClaw, or both)
"""

from typing import List
from models.core import JobPosting, JobSearchRequest, JobSource, AgentState
from mcp_tools.brave_search_mcp import get_brave_search_tool
from mcp_tools.openclaw_mcp import get_openclaw_tool
from core.logger import get_logger

logger = get_logger("job_autopilot.agents.search_agent")


class JobSearchAgent:
    """
    Responsible for searching job postings based on user query
    Supports multiple search backends:
    - Brave Search MCP tool
    - OpenClaw MCP tool
    - Combined results from both sources
    """
    
    def __init__(self, max_results: int = 15):
        self.max_results = max_results
        self.brave_search_tool = get_brave_search_tool()
        self.openclaw_tool = get_openclaw_tool()
    
    async def invoke(self, state: AgentState) -> AgentState:
        """
        Execute job search using configured source(s)
        
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
                "input_source": request.input_source,
                "job_source": request.job_source
            }
        )
        
        try:
            job_postings = []
            
            # Route to appropriate search backend(s)
            if request.job_source == JobSource.BRAVE_SEARCH:
                logger.info("Using Brave Search backend")
                job_postings = await self.brave_search_tool.search(
                    query=request.query,
                    count=self.max_results
                )
            
            elif request.job_source == JobSource.OPENCLAW:
                logger.info("Using OpenClaw backend")
                job_postings = await self.openclaw_tool.search(
                    query=request.query,
                    count=self.max_results
                )
            
            elif request.job_source == JobSource.BOTH:
                logger.info("Using both Brave Search and OpenClaw backends")
                # Divide results between sources
                results_per_source = max(1, self.max_results // 2)
                
                brave_jobs = await self.brave_search_tool.search(
                    query=request.query,
                    count=results_per_source
                )
                
                openclaw_jobs = await self.openclaw_tool.search(
                    query=request.query,
                    count=results_per_source
                )
                
                job_postings = brave_jobs + openclaw_jobs
                logger.info(
                    "Combined search results",
                    extra={
                        "brave_search_count": len(brave_jobs),
                        "openclaw_count": len(openclaw_jobs),
                        "total_count": len(job_postings)
                    }
                )
            
            else:
                logger.warning(
                    "Unknown job source, defaulting to Brave Search",
                    extra={"job_source": request.job_source}
                )
                job_postings = await self.brave_search_tool.search(
                    query=request.query,
                    count=self.max_results
                )
            
            logger.info(
                "Job search completed",
                extra={
                    "query": request.query,
                    "source": request.job_source,
                    "results_count": len(job_postings)
                }
            )
            
            # Update state
            state.job_postings = job_postings
            
            if not job_postings:
                logger.warning(
                    "No jobs found for query",
                    extra={
                        "query": request.query,
                        "source": request.job_source
                    }
                )
                state.errors.append(f"No jobs found for query: {request.query}")
            
            return state
        
        except Exception as e:
            logger.error(
                "Job search failed",
                extra={
                    "query": request.query,
                    "source": request.job_source,
                    "error": str(e)
                },
                exc_info=True
            )
            state.errors.append(f"Job search error: {str(e)}")
            return state


def create_job_search_agent(max_results: int = 15) -> JobSearchAgent:
    """Factory function to create Job Search Agent"""
    return JobSearchAgent(max_results=max_results)
