from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from ...services.resume_tailor import tailor_resume
from ...models.tailored_resume import TailoredResume

router = APIRouter(prefix="/resume", tags=["resume"])

class TailorRequest(BaseModel):
    parsed_resume: dict
    target_role: str
    target_company: str = ""

class TailorResponse(BaseModel):
    tailored_resume: TailoredResume
    match_score: float = Field(..., ge=0, le=100, description="Estimated ATS/resume match %")
    visa_advice: str

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

        # Generate visa advice based on education level
        visa_advice = generate_visa_advice(request.parsed_resume.get("education", []))

        return TailorResponse(
            tailored_resume=tailored,
            match_score=match_score,
            visa_advice=visa_advice
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tailoring failed: {str(e)}")


def calculate_match_score(resume_skills: list, tailored_skills: list) -> float:
    """Calculate skill alignment score 0-100."""
    if not resume_skills or not tailored_skills:
        return 50.0

    resume_skill_items = set()
    for skill_cat in resume_skills:
        if isinstance(skill_cat, dict):
            resume_skill_items.update(skill_cat.get("items", []))

    matched = sum(1 for skill in tailored_skills if skill in resume_skill_items)
    return min(100.0, (matched / len(tailored_skills)) * 100) if tailored_skills else 50.0


def generate_visa_advice(education: list) -> str:
    if not education:
        return "⚠️ Verify education details for Stamp 1G eligibility."

    max_nfq = max([edu.get("nfq_level", 0) for edu in education if edu.get("nfq_level")], default=0)
    grad_year = max([int(edu.get("year", "0").split("-")[-1]) for edu in education if edu.get("year")], default=0)

    is_recent = grad_year >= 2025  # 2026 context, within 12 months

    if max_nfq >= 9:
        months = 24
        threshold = "€36,848 (Graduate Band – recent grads) or €40,904 (standard)"
    elif max_nfq == 8:
        months = 12
        threshold = "€34,009 (Graduate Band) or €36,605 (standard)"
    else:
        return "⚠️ Stamp 1G typically requires NFQ Level 8+ (Honours Bachelor or higher)."

    return f"✅ Eligible for **{months}-month Stamp 1G** ({'recent graduate' if is_recent else 'standard'}). CSEP threshold: {threshold}."
