"""
Curation Agent - Analyzes jobs and selects best matches
Queries Mem0 for user skills and selects LaTeX template
"""

from typing import Optional, List
from models.core import (
    AgentState, CurationResult, TemplateType, UserProfile
)
from core.logger import get_logger
from core.llm_provider import invoke_llm_with_system_prompt

logger = get_logger("job_autopilot.agents.curation_agent")


class CurationAgent:
    """
    Responsible for:
    - Querying Mem0 for user skills/experience
    - Analyzing job requirements
    - Computing job-fit score
    - Selecting appropriate LaTeX template
    - Identifying key requirements to highlight
    """
    
    def __init__(self):
        self.templates = {
            "python": TemplateType.SWE,
            "backend": TemplateType.SWE,
            "frontend": TemplateType.SWE,
            "fullstack": TemplateType.SWE,
            "swe": TemplateType.SWE,
            "software": TemplateType.SWE,
            "devops": TemplateType.DEVOPS,
            "infrastructure": TemplateType.DEVOPS,
            "sre": TemplateType.DEVOPS,
            "kubernetes": TemplateType.DEVOPS,
            "ml": TemplateType.ML,
            "machine learning": TemplateType.ML,
            "data science": TemplateType.ML,
            "ai": TemplateType.ML,
        }
    
    async def invoke(self, state: AgentState) -> AgentState:
        """
        Execute curation analysis
        
        Args:
            state: Current agent state with job_postings
        
        Returns:
            Updated state with selected_job and curation_result
        """
        if not state.job_postings:
            logger.warning("No job postings to curate")
            state.errors.append("No job postings available for curation")
            return state
        
        logger.info(
            "Curation Agent invoked",
            extra={
                "job_postings_count": len(state.job_postings),
                "user_id": state.job_search_request.user_id
            }
        )
        
        try:
            # Get user profile (mock Mem0 for now)
            user_profile = await self._get_user_profile(
                state.job_search_request.user_id
            )
            
            # Score all jobs and select best match
            best_job = None
            best_score = 0
            best_curation = None
            
            for job in state.job_postings:
                score = await self._compute_fit_score(job, user_profile)
                logger.debug(
                    "Job fit score computed",
                    extra={
                        "job_id": job.id,
                        "job_title": job.title,
                        "fit_score": score
                    }
                )
                
                if score > best_score:
                    best_score = score
                    best_job = job
            
            if best_job:
                # Create curation result for best job
                template_type = self._select_template(best_job)
                key_requirements = await self._extract_key_requirements(
                    best_job, user_profile
                )
                
                curation_result = CurationResult(
                    selected_job=best_job,
                    fit_score=best_score,
                    template_type=template_type,
                    user_skills=user_profile.skills,
                    key_requirements=key_requirements
                )
                
                state.selected_job = best_job
                state.curation_result = curation_result
                
                logger.info(
                    "Job curation completed",
                    extra={
                        "selected_job_id": best_job.id,
                        "selected_job_title": best_job.title,
                        "fit_score": best_score,
                        "template_type": template_type.value
                    }
                )
            else:
                logger.warning("No suitable job found for curation")
                state.errors.append("Unable to find suitable job match")
            
            return state
        
        except Exception as e:
            logger.error(
                "Curation failed",
                extra={"error": str(e)},
                exc_info=True
            )
            state.errors.append(f"Curation error: {str(e)}")
            return state
    
    async def _get_user_profile(self, user_id: str) -> UserProfile:
        """
        Fetch user profile from Mem0
        (Mock implementation for now)
        """
        logger.debug("Fetching user profile from Mem0", extra={"user_id": user_id})
        
        # Mock user profile
        return UserProfile(
            user_id=user_id,
            name="John Doe",
            skills=[
                "Python",
                "Go",
                "Kubernetes",
                "Docker",
                "AWS",
                "PostgreSQL",
                "React",
                "TypeScript",
                "System Design",
                "Microservices"
            ],
            experience=[
                {
                    "role": "Senior Backend Engineer",
                    "company": "Tech Corp",
                    "duration": "3 years",
                    "description": "Led backend systems, worked with Kubernetes, Go"
                },
                {
                    "role": "Software Engineer",
                    "company": "Startup Inc",
                    "duration": "2 years",
                    "description": "Full stack development, Python, React"
                }
            ],
            education=[
                {
                    "degree": "B.S. Computer Science",
                    "school": "University",
                    "year": 2019
                }
            ],
            certifications=["AWS Solutions Architect", "CKA"],
            preferences={
                "preferred_roles": ["Backend", "DevOps", "SRE"],
                "preferred_locations": ["San Francisco", "Remote"],
                "min_salary": 150000
            }
        )
    
    async def _compute_fit_score(
        self,
        job,
        user_profile: UserProfile
    ) -> float:
        """
        Compute job-fit score using LLM
        Analyzes job requirements vs user skills
        """
        prompt = f"""
Analyze how well this job matches the candidate's profile.
Return a fit score from 0-100.

Job Title: {job.title}
Job Description: {job.description}

Candidate Skills: {', '.join(user_profile.skills)}
Candidate Experience: {user_profile.experience}

Provide ONLY a single number between 0 and 100 representing the fit score.
Consider skill match, seniority level, and role alignment.
"""
        
        try:
            response = await invoke_llm_with_system_prompt(
                system_prompt="You are an expert recruiter analyzing job fit.",
                user_prompt=prompt
            )
            
            # Extract number from response
            score_text = ''.join(c for c in response if c.isdigit())
            score = float(score_text[:3]) if score_text else 50.0
            return min(100, max(0, score))
        
        except Exception as e:
            logger.warning(
                "Failed to compute fit score with LLM, using heuristic",
                extra={"error": str(e)}
            )
            # Fallback: simple heuristic
            matching_skills = sum(
                1 for skill in user_profile.skills
                if skill.lower() in job.description.lower()
            )
            return (matching_skills / len(user_profile.skills)) * 100 if user_profile.skills else 50.0
    
    def _select_template(self, job) -> TemplateType:
        """
        Select LaTeX template based on job description
        """
        job_text = f"{job.title} {job.description}".lower()
        
        for keyword, template_type in self.templates.items():
            if keyword in job_text:
                logger.debug(
                    "Template selected",
                    extra={
                        "keyword": keyword,
                        "template": template_type.value
                    }
                )
                return template_type
        
        # Default to SWE
        return TemplateType.SWE
    
    async def _extract_key_requirements(
        self,
        job,
        user_profile: UserProfile
    ) -> List[str]:
        """
        Extract key requirements that match user skills
        """
        prompt = f"""
Extract the top 5 key requirements from this job description that the candidate should highlight on their resume.
The candidate has these skills: {', '.join(user_profile.skills)}

Job Description: {job.description}

Return a JSON array of strings with exactly 5 requirements.
Format: ["requirement1", "requirement2", "requirement3", "requirement4", "requirement5"]
"""
        
        try:
            response = await invoke_llm_with_system_prompt(
                system_prompt="You are an expert job analyst.",
                user_prompt=prompt
            )
            
            # Parse JSON array from response
            import json
            import re
            
            # Extract JSON array from response
            match = re.search(r'\[.*?\]', response, re.DOTALL)
            if match:
                requirements = json.loads(match.group())
                return requirements[:5]
        
        except Exception as e:
            logger.warning(
                "Failed to extract requirements with LLM",
                extra={"error": str(e)}
            )
        
        # Fallback: return generic requirements
        return [
            job.title,
            "Strong system design skills",
            "Experience with cloud platforms",
            "Team collaboration",
            "Problem-solving"
        ]


def create_curation_agent() -> CurationAgent:
    """Factory function to create Curation Agent"""
    return CurationAgent()
