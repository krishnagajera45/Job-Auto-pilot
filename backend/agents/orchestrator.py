"""
Orchestrator - LangGraph workflow combining all agents
Orchestrates the entire job application pipeline
"""

from typing import Optional
from langgraph.graph import StateGraph, END
from models.core import AgentState, JobSearchRequest, InputSource, JobSource
from agents.search_agent import create_job_search_agent
from agents.curation_agent import create_curation_agent
from agents.generation_agent import create_resume_generation_agent
from agents.compilation_agent import create_compilation_agent
from agents.notification_agent import create_notification_agent
from core.logger import get_logger

logger = get_logger("job_autopilot.orchestrator")


class JobApplicationOrchestrator:
    """
    LangGraph-based orchestrator for the entire job application workflow
    Chains agents: Search → Curation → Generation → Compilation → Notification
    """
    
    def __init__(self):
        self.search_agent = create_job_search_agent()
        self.curation_agent = create_curation_agent()
        self.generation_agent = create_resume_generation_agent()
        self.compilation_agent = create_compilation_agent()
        self.notification_agent = create_notification_agent()
        
        # Build LangGraph workflow
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """
        Build LangGraph workflow
        
        Flow:
        Search → Curation → Generation → Compilation → Notification → END
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("search", self._search_node)
        workflow.add_node("curation", self._curation_node)
        workflow.add_node("generation", self._generation_node)
        workflow.add_node("compilation", self._compilation_node)
        workflow.add_node("notification", self._notification_node)
        
        # Add edges
        workflow.add_edge("search", "curation")
        workflow.add_edge("curation", "generation")
        workflow.add_edge("generation", "compilation")
        workflow.add_edge("compilation", "notification")
        workflow.add_edge("notification", END)
        
        # Set entry point
        workflow.set_entry_point("search")
        
        logger.info("LangGraph workflow built successfully")
        
        return workflow.compile()
    
    async def _search_node(self, state: AgentState) -> AgentState:
        """Execute search agent node"""
        logger.debug("Executing search node")
        return await self.search_agent.invoke(state)
    
    async def _curation_node(self, state: AgentState) -> AgentState:
        """Execute curation agent node"""
        logger.debug("Executing curation node")
        return await self.curation_agent.invoke(state)
    
    async def _generation_node(self, state: AgentState) -> AgentState:
        """Execute generation agent node"""
        logger.debug("Executing generation node")
        return await self.generation_agent.invoke(state)
    
    async def _compilation_node(self, state: AgentState) -> AgentState:
        """Execute compilation agent node"""
        logger.debug("Executing compilation node")
        return await self.compilation_agent.invoke(state)
    
    async def _notification_node(self, state: AgentState) -> AgentState:
        """Execute notification agent node"""
        logger.debug("Executing notification node")
        return await self.notification_agent.invoke(state)
    
    async def invoke(
        self,
        query: str,
        user_id: str,
        input_source: InputSource = InputSource.WHATSAPP,
        job_source: Optional['JobSource'] = None
    ) -> AgentState:
        """
        Execute the entire workflow
        
        Args:
            query: Search query or job link
            user_id: User ID
            input_source: Source of input (whatsapp, job_link, scheduled)
            job_source: Preferred job search source (brave_search, openclaw, both)
        
        Returns:
            Final agent state with all results
        """
        logger.info(
            "Starting Job Application Workflow",
            extra={
                "query": query,
                "user_id": user_id,
                "input_source": input_source.value
            }
        )
        
        # Import JobSource here to avoid circular imports
        if job_source is None:
            job_source = JobSource.BRAVE_SEARCH
        
        # Initialize state
        request = JobSearchRequest(
            query=query,
            user_id=user_id,
            input_source=input_source,
            job_source=job_source,
            original_message=query
        )
        
        initial_state = AgentState(
            job_search_request=request
        )
        
        logger.info(
            "Starting Job Application Workflow",
            extra={
                "query": query[:50],
                "user_id": user_id,
                "input_source": input_source.value,
                "job_source": request.job_source.value
            }
        )
        
        # Execute workflow
        # Note: LangGraph's async execution needs proper implementation
        # For now, we'll run agents sequentially
        state = initial_state
        
        try:
            state = await self.search_agent.invoke(state)
            if state.errors:
                logger.warning("Search agent errors", extra={"errors": state.errors})
            
            state = await self.curation_agent.invoke(state)
            if state.errors:
                logger.warning("Curation agent errors", extra={"errors": state.errors})
            
            state = await self.generation_agent.invoke(state)
            if state.errors:
                logger.warning("Generation agent errors", extra={"errors": state.errors})
            
            state = await self.compilation_agent.invoke(state)
            if state.errors:
                logger.warning("Compilation agent errors", extra={"errors": state.errors})
            
            state = await self.notification_agent.invoke(state)
            if state.errors:
                logger.warning("Notification agent errors", extra={"errors": state.errors})
            
            logger.info(
                "Workflow completed",
                extra={
                    "user_id": user_id,
                    "total_errors": len(state.errors),
                    "has_pdf": state.resume_pdf_path is not None
                }
            )
            
            return state
        
        except Exception as e:
            logger.error(
                "Workflow execution failed",
                extra={"error": str(e)},
                exc_info=True
            )
            state.errors.append(f"Workflow error: {str(e)}")
            return state


# Singleton instance
_orchestrator = None


def get_orchestrator() -> JobApplicationOrchestrator:
    """Get or create orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = JobApplicationOrchestrator()
    return _orchestrator


async def run_workflow(
    query: str,
    user_id: str,
    input_source: InputSource = InputSource.WHATSAPP,
    job_source: Optional['JobSource'] = None
) -> AgentState:
    """
    Convenience function to run the entire workflow
    
    Args:
        query: Search query or job link
        user_id: User identifier
        input_source: Source of the input (WhatsApp, job link, scheduled)
        job_source: Preferred job search source (Brave Search, OpenClaw, or both)
    """
    from models.core import JobSource
    
    if job_source is None:
        job_source = JobSource.BRAVE_SEARCH
    
    orchestrator = get_orchestrator()
    return await orchestrator.invoke(query, user_id, input_source, job_source)
