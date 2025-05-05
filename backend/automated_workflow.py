import os
import requests
from langchain.llms.base import LLM
from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain
from fastapi import APIRouter

# Custom LLM wrapper for Groq API
class GroqLLM(LLM):
    def __init__(self, api_key: str):
        self.api_key = api_key

    @property
    def _llm_type(self):
        return "groq"

    def _call(self, prompt: str, stop: list = None):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 8192,
        }
        response = requests.post("https://api.groq.com/v1/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


def search_jobs(preferences):
    url = "https://jobs-api14.p.rapidapi.com/v2/list"
    headers = {
        "X-RapidAPI-Key": os.environ.get("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "jobs-api14.p.rapidapi.com"
    }
    params = {
        "query": preferences.get("role"),
        "location": preferences.get("location"),
        "employmentTypes": "fulltime;parttime" if preferences.get("remote") else "fulltime",
        "datePosted": "month",
        "remoteOnly": "true" if preferences.get("remote") else "false"
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("jobs", [])


# Define LangChain workflow for job application automation
class JobApplicationWorkflow:
    def __init__(self):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set.")
        self.llm = GroqLLM(api_key=api_key)

    def run(self, preferences):
        # Step 1: Job Search
        job_search_prompt = PromptTemplate(
            input_variables=["preferences"],
            template="Search for jobs based on the following preferences: {preferences}. Return a list of job titles."
        )
        job_search_chain = SequentialChain(
            llm=self.llm,
            prompt=job_search_prompt,
            output_key="job_list"
        )
        job_list = job_search_chain.run(preferences=preferences)

        # Step 2: Resume Tailoring using the /tailor API
        tailored_resumes = []
        for job in job_list:
            response = requests.post(
                "http://127.0.0.1:8000/tailor",
                json={
                    "job_description": job,
                    "resume": preferences.get("resume"),
                    "cover_letter": preferences.get("cover_letter", "")
                }
            )
            response.raise_for_status()
            tailored_resumes.append(response.json())

        # Step 3: Application Submission
        submission_results = []
        for application in tailored_resumes:
            submission_prompt = PromptTemplate(
                input_variables=["application"],
                template="Submit the following application: {application}. Return the submission status."
            )
            submission_chain = SequentialChain(
                llm=self.llm,
                prompt=submission_prompt,
                output_key="submission_status"
            )
            submission_results.append(submission_chain.run(application=application))

        return submission_results

router = APIRouter()

@router.post("/apply")
def apply_for_jobs(preferences: dict):
    workflow = JobApplicationWorkflow()
    results = workflow.run(preferences)
    return {"applications": results}