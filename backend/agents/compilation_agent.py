"""
Compilation Agent - Compiles LaTeX to PDF
Includes error handling with LLM self-correction loop
"""

import os
from models.core import AgentState
from mcp_tools.latex_compiler_mcp import (
    get_latex_compiler_tool,
    LaTeXCompilationError
)
from core.logger import get_logger
from core.llm_provider import invoke_llm_with_system_prompt
from config.settings import settings

logger = get_logger("job_autopilot.agents.compilation_agent")


class CompilationAgent:
    """
    Responsible for:
    - Compiling LaTeX to PDF
    - Error handling with LLM self-correction
    - Retry mechanism (max 3 attempts)
    """
    
    MAX_RETRIES = 3
    
    def __init__(self):
        self.compiler = get_latex_compiler_tool()
        self.output_dir = settings.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def invoke(self, state: AgentState) -> AgentState:
        """
        Compile LaTeX to PDF with error handling
        
        Args:
            state: Current agent state with resume_latex
        
        Returns:
            Updated state with resume_pdf_path
        """
        if not state.resume_latex:
            logger.warning("No resume LaTeX available for compilation")
            state.errors.append("Missing LaTeX code for compilation")
            return state
        
        logger.info(
            "Compilation Agent invoked",
            extra={
                "latex_size_bytes": len(state.resume_latex)
            }
        )
        
        try:
            # Attempt compilation with retry and self-correction
            user_id = state.job_search_request.user_id
            job_id = state.selected_job.id
            filename = f"resume_{user_id}_{job_id}"
            
            # Save LaTeX to file
            tex_path = os.path.join(self.output_dir, f"{filename}.tex")
            with open(tex_path, 'w') as f:
                f.write(state.resume_latex)
            
            logger.debug("LaTeX file written", extra={"path": tex_path})
            
            # Compile with retry loop
            pdf_path = await self._compile_with_retry(
                tex_path=tex_path,
                latex_code=state.resume_latex,
                filename=filename
            )
            
            state.resume_pdf_path = pdf_path
            
            logger.info(
                "Resume PDF generated successfully",
                extra={
                    "pdf_path": pdf_path,
                    "filename": filename
                }
            )
            
            return state
        
        except Exception as e:
            logger.error(
                "Resume compilation failed after retries",
                extra={"error": str(e)},
                exc_info=True
            )
            state.errors.append(f"Resume compilation error: {str(e)}")
            return state
    
    async def _compile_with_retry(
        self,
        tex_path: str,
        latex_code: str,
        filename: str
    ) -> str:
        """
        Compile LaTeX with retry and self-correction
        """
        current_latex = latex_code
        
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(
                    f"Compilation attempt {attempt + 1}/{self.MAX_RETRIES}",
                    extra={"tex_file": tex_path}
                )
                
                # Write current version to file
                with open(tex_path, 'w') as f:
                    f.write(current_latex)
                
                # Attempt compilation
                pdf_path = await self.compiler.compile(
                    tex_file_path=tex_path,
                    output_filename=filename
                )
                
                logger.info(
                    "LaTeX compilation successful",
                    extra={
                        "pdf_path": pdf_path,
                        "attempt": attempt + 1
                    }
                )
                
                return pdf_path
            
            except LaTeXCompilationError as e:
                logger.warning(
                    f"LaTeX compilation error on attempt {attempt + 1}",
                    extra={
                        "error": str(e),
                        "error_details": e.error_details,
                        "attempt": attempt + 1
                    }
                )
                
                # If this is the last attempt, raise error
                if attempt == self.MAX_RETRIES - 1:
                    raise LaTeXCompilationError(
                        f"LaTeX compilation failed after {self.MAX_RETRIES} attempts",
                        error_details=e.error_details
                    )
                
                # Try to fix LaTeX using LLM
                logger.info(
                    "Attempting LLM-based error correction",
                    extra={"attempt": attempt + 1}
                )
                
                current_latex = await self._fix_latex_with_llm(
                    latex_code=current_latex,
                    error_message=str(e),
                    error_details=e.error_details
                )
    
    async def _fix_latex_with_llm(
        self,
        latex_code: str,
        error_message: str,
        error_details: str
    ) -> str:
        """
        Use LLM to analyze and fix LaTeX compilation errors
        """
        prompt = f"""
The LaTeX code below failed to compile with this error:

Error: {error_message}
Details: {error_details}

Fix the LaTeX code to resolve the compilation error.
Output ONLY the corrected LaTeX code, nothing else.

Original LaTeX:
{latex_code}

Corrected LaTeX:
"""
        
        system_prompt = """You are a LaTeX expert. Analyze the compilation error and fix the LaTeX code.
Ensure the output is valid LaTeX that can compile successfully.
Output ONLY the complete LaTeX code without any explanations or markdown formatting.
"""
        
        try:
            fixed_latex = await invoke_llm_with_system_prompt(
                system_prompt=system_prompt,
                user_prompt=prompt
            )
            
            logger.debug(
                "LLM provided LaTeX fix",
                extra={"fixed_code_size": len(fixed_latex)}
            )
            
            # Clean up response (remove markdown code blocks if present)
            if "```" in fixed_latex:
                parts = fixed_latex.split("```")
                if len(parts) >= 3:
                    fixed_latex = parts[1]
                    if fixed_latex.startswith("latex") or fixed_latex.startswith("tex"):
                        fixed_latex = fixed_latex[5:].lstrip()
            
            return fixed_latex
        
        except Exception as e:
            logger.error(
                "LLM-based error correction failed",
                extra={"error": str(e)},
                exc_info=True
            )
            # Return original if LLM fix fails
            return latex_code


def create_compilation_agent() -> CompilationAgent:
    """Factory function to create Compilation Agent"""
    return CompilationAgent()
