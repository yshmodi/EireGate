from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from ...services.resume_tailor import tailor_resume, calculate_match_score
from ...models.tailored_resume import TailoredResume

router = APIRouter(prefix="/resume", tags=["resume"])


class TailorRequest(BaseModel):
    parsed_resume: dict
    target_role: str
    target_company: str = ""


class TailorResponse(BaseModel):
    tailored_resume: TailoredResume
    match_score: float = Field(..., ge=0, le=100, description="Estimated skill match %")


@router.post("/tailor", response_model=TailorResponse)
async def tailor_resume_endpoint(request: TailorRequest):
    try:
        tailored = tailor_resume(
            request.parsed_resume,
            request.target_role,
            request.target_company
        )

        # Calculate match score based on skill alignment
        match_score = calculate_match_score(
            request.parsed_resume.get("skills", []),
            tailored.key_skills
        )

        return TailorResponse(
            tailored_resume=tailored,
            match_score=match_score
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tailoring failed: {str(e)}")
