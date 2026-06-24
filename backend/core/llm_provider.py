"""
LLM Provider for Ollama with LangChain integration
"""

import asyncio
from typing import Optional
from langchain_community.llms import Ollama
from langchain_core.language_model import LLM
from config.settings import settings
from core.logger import get_logger

logger = get_logger("job_autopilot.llm_provider")


class LLMProvider:
    """
    Manages LLM connection to Ollama
    Provides both sync and async interfaces
    """
    
    _instance: Optional["LLMProvider"] = None
    _llm: Optional[LLM] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self) -> LLM:
        """Initialize LLM connection to Ollama"""
        if self._llm is not None:
            return self._llm
        
        logger.info(
            "Initializing Ollama LLM",
            extra={
                "base_url": settings.OLLAMA_BASE_URL,
                "model": settings.OLLAMA_MODEL
            }
        )
        
        try:
            self._llm = Ollama(
                base_url=settings.OLLAMA_BASE_URL,
                model=settings.OLLAMA_MODEL,
                temperature=0.7,
                num_ctx=8192,  # Context window
            )
            
            logger.info("Ollama LLM initialized successfully")
            return self._llm
            
        except Exception as e:
            logger.error(
                "Failed to initialize Ollama LLM",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
    
    async def invoke(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Invoke LLM with prompt (async-compatible)
        
        Args:
            prompt: Input prompt
            temperature: Override default temperature
            max_tokens: Max tokens in response
        
        Returns:
            LLM response text
        """
        if self._llm is None:
            await self.initialize()
        
        logger.debug(
            "Invoking LLM",
            extra={
                "prompt_length": len(prompt),
                "model": settings.OLLAMA_MODEL
            }
        )
        
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._llm.invoke(prompt)
            )
            
            logger.debug(
                "LLM response received",
                extra={
                    "response_length": len(response),
                    "input_tokens": len(prompt.split()),
                    "output_tokens": len(response.split())
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "LLM invocation failed",
                extra={"error": str(e)},
                exc_info=True
            )
            raise
    
    async def invoke_with_system_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None
    ) -> str:
        """
        Invoke LLM with system and user prompts
        
        Args:
            system_prompt: System role/instructions
            user_prompt: User query
            temperature: Temperature setting
        
        Returns:
            LLM response
        """
        full_prompt = f"""System: {system_prompt}

User: {user_prompt}

Response:"""
        return await self.invoke(full_prompt, temperature)


# Singleton instance
_llm_provider = LLMProvider()


async def get_llm() -> LLM:
    """Get LLM instance (singleton)"""
    await _llm_provider.initialize()
    return _llm_provider._llm


async def invoke_llm(prompt: str) -> str:
    """Convenience function to invoke LLM"""
    return await _llm_provider.invoke(prompt)


async def invoke_llm_with_system_prompt(
    system_prompt: str,
    user_prompt: str
) -> str:
    """Convenience function to invoke LLM with system prompt"""
    return await _llm_provider.invoke_with_system_prompt(system_prompt, user_prompt)
