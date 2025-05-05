import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from groq import Groq

# Initialize Groq client securely using environment variable
client = Groq(api_key="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")

router = APIRouter()

class TailorRequest(BaseModel):
    job_description: str
    resume: str
    cover_letter: Optional[str] = None

@router.post("/tailor")
def tailor_documents(request: TailorRequest):
    messages = [
        {"role": "system", "content": "You are an AI assistant that specializes in tailoring resumes and cover letters. Your goal is to refine and optimize the provided resume and cover letter to align perfectly with the job description. Ensure the output is professional, concise, and highlights the candidate's strengths relevant to the job. Always separate the refined resume and cover letter clearly in the output."},
        {"role": "user", "content": f"Job Description: {request.job_description}"},
        {"role": "user", "content": f"Resume: {request.resume}"},
    ]

    if request.cover_letter:
        messages.append({"role": "user", "content": f"Cover Letter: {request.cover_letter}"})

    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=messages,
            temperature=0.75,
            max_completion_tokens=8192,
            top_p=1,
            stream=False,
            stop=None,
        )

        # Debugging: Print the response structure
        print("Groq API Response:", completion)

        # Extract tailored content for both resume and cover letter
        if hasattr(completion, "choices") and len(completion.choices) > 0:
            tailored_content = completion.choices[0].message.content
        else:
            raise ValueError("Unexpected response format from Groq API")

        # Post-process the tailored content to split resume and cover letter
        tailored_resume = None
        tailored_cover_letter = None

        if "**Refined Resume:**" in tailored_content and "**Cover Letter:**" in tailored_content:
            parts = tailored_content.split("**Cover Letter:**")
            tailored_resume = parts[0].replace("**Refined Resume:**", "").strip()
            tailored_cover_letter = parts[1].strip()
        else:
            raise ValueError("Failed to split resume and cover letter from the response.")

        return {
            "tailored_resume": tailored_resume,
            "tailored_cover_letter": tailored_cover_letter,
        }

    except Exception as e:
        print("Error while processing Groq API response:", str(e))
        raise HTTPException(status_code=500, detail="Failed to process Groq API response")