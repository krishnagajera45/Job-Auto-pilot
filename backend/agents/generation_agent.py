"""
Resume Generation Agent - Generates LaTeX resume
Uses LLM to create role-specific resume
"""

import os
from models.core import AgentState
from core.logger import get_logger
from core.llm_provider import invoke_llm_with_system_prompt
from config.settings import settings

logger = get_logger("job_autopilot.agents.generation_agent")


# LaTeX resume templates
RESUME_TEMPLATES = {
    "swe": r"""
\documentclass[11pt]{article}
\usepackage[utf-8]{inputenc}
\usepackage[margin=0.5in]{geometry}
\usepackage{hyperref}
\usepackage{xcolor}

\begin{document}

\noindent
\textbf{\Large {NAME}} \\
Email: {EMAIL} | Phone: {PHONE} | LinkedIn: {LINKEDIN} | GitHub: {GITHUB} \\

\noindent\rule{\textwidth}{0.4pt}

\section*{PROFESSIONAL SUMMARY}
{SUMMARY}

\section*{TECHNICAL SKILLS}
{SKILLS}

\section*{PROFESSIONAL EXPERIENCE}
{EXPERIENCE}

\section*{EDUCATION}
{EDUCATION}

\section*{CERTIFICATIONS}
{CERTIFICATIONS}

\end{document}
""",
    "devops": r"""
\documentclass[11pt]{article}
\usepackage[utf-8]{inputenc}
\usepackage[margin=0.5in]{geometry}
\usepackage{hyperref}

\begin{document}

\noindent
\textbf{\Large {NAME}} \\
Email: {EMAIL} | Phone: {PHONE} | LinkedIn: {LINKEDIN} \\

\noindent\rule{\textwidth}{0.4pt}

\section*{PROFESSIONAL SUMMARY}
{SUMMARY}

\section*{CORE COMPETENCIES}
{SKILLS}

\section*{PROFESSIONAL EXPERIENCE}
{EXPERIENCE}

\section*{CERTIFICATIONS}
{CERTIFICATIONS}

\section*{EDUCATION}
{EDUCATION}

\end{document}
""",
    "ml": r"""
\documentclass[11pt]{article}
\usepackage[utf-8]{inputenc}
\usepackage[margin=0.5in]{geometry}
\usepackage{hyperref}

\begin{document}

\noindent
\textbf{\Large {NAME}} \\
Email: {EMAIL} | Phone: {PHONE} | LinkedIn: {LINKEDIN} | GitHub: {GITHUB} \\

\noindent\rule{\textwidth}{0.4pt}

\section*{PROFESSIONAL SUMMARY}
{SUMMARY}

\section*{MACHINE LEARNING SKILLS}
{SKILLS}

\section*{PROFESSIONAL EXPERIENCE}
{EXPERIENCE}

\section*{PROJECTS}
{PROJECTS}

\section*{EDUCATION}
{EDUCATION}

\section*{CERTIFICATIONS}
{CERTIFICATIONS}

\end{document}
"""
}


class ResumeGenerationAgent:
    """
    Responsible for generating LaTeX resume
    Tailored to specific job using LLM
    """
    
    def __init__(self):
        self.templates = RESUME_TEMPLATES
        self.output_dir = settings.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def invoke(self, state: AgentState) -> AgentState:
        """
        Generate resume LaTeX
        
        Args:
            state: Current agent state with curation_result
        
        Returns:
            Updated state with resume_latex
        """
        if not state.curation_result or not state.selected_job:
            logger.warning("No curation result or job available")
            state.errors.append("Missing curation result for resume generation")
            return state
        
        logger.info(
            "Resume Generation Agent invoked",
            extra={
                "job_id": state.selected_job.id,
                "template_type": state.curation_result.template_type.value
            }
        )
        
        try:
            # Generate resume LaTeX
            resume_latex = await self._generate_resume_latex(state)
            
            # Save to file
            user_id = state.job_search_request.user_id
            job_id = state.selected_job.id
            filename = f"resume_{user_id}_{job_id}"
            tex_path = os.path.join(self.output_dir, f"{filename}.tex")
            
            with open(tex_path, 'w') as f:
                f.write(resume_latex)
            
            state.resume_latex = resume_latex
            
            logger.info(
                "Resume LaTeX generated and saved",
                extra={
                    "filename": filename,
                    "path": tex_path,
                    "size_bytes": len(resume_latex)
                }
            )
            
            return state
        
        except Exception as e:
            logger.error(
                "Resume generation failed",
                extra={"error": str(e)},
                exc_info=True
            )
            state.errors.append(f"Resume generation error: {str(e)}")
            return state
    
    async def _generate_resume_latex(self, state: AgentState) -> str:
        """
        Generate LaTeX resume using LLM
        """
        curation = state.curation_result
        job = state.selected_job
        template_type = curation.template_type.value
        
        # Get base template
        base_template = self.templates.get(template_type, self.templates["swe"])
        
        # Create generation prompt
        prompt = f"""
You are an expert resume writer. Generate a professional resume in LaTeX format.

Job Title: {job.title}
Company: {job.company}
Job Description: {job.description}

Candidate Skills: {', '.join(curation.user_skills)}
Key Requirements to Highlight: {', '.join(curation.key_requirements)}

Generate the complete resume with:
1. Professional summary tailored to the job
2. Technical skills section (formatted as bullet points)
3. Professional experience (2-3 most relevant roles)
4. Education
5. Certifications

Output ONLY valid LaTeX code. NO markdown, NO explanations.
Make sure the resume is ATS-optimized and highlights the key requirements.

Base the formatting on this template structure:
{base_template}

Replace the placeholders with actual content. 
Output ONLY the complete LaTeX code.
"""
        
        logger.debug(
            "Sending resume generation prompt to LLM",
            extra={
                "job_title": job.title,
                "template_type": template_type
            }
        )
        
        system_prompt = """You are a LaTeX expert and professional resume writer. 
Generate only valid LaTeX code without any markdown formatting or explanations.
Ensure all special characters in the resume are properly escaped for LaTeX.
"""
        
        response = await invoke_llm_with_system_prompt(
            system_prompt=system_prompt,
            user_prompt=prompt
        )
        
        # Extract LaTeX code (remove markdown code blocks if present)
        latex_code = response
        if "```" in latex_code:
            # Extract content between ``` markers
            parts = latex_code.split("```")
            if len(parts) >= 3:
                latex_code = parts[1]
                # Remove language specifier if present
                if latex_code.startswith("latex") or latex_code.startswith("tex"):
                    latex_code = latex_code[5:].lstrip()
        
        # Validate LaTeX structure
        if not latex_code.strip().startswith("\\documentclass"):
            logger.warning("Generated LaTeX doesn't start with \\documentclass")
            latex_code = base_template + "\n" + latex_code
        
        return latex_code


def create_resume_generation_agent() -> ResumeGenerationAgent:
    """Factory function to create Resume Generation Agent"""
    return ResumeGenerationAgent()
