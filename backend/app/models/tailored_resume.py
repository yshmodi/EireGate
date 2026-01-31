from pydantic import BaseModel, Field
from typing import List

class TailoredResume(BaseModel):
    professional_summary: str = Field(..., description="4-6 sentence ATS-friendly summary")
    achievement_bullets: List[str] = Field(..., min_length=5, max_length=7)
    key_skills: List[str] = Field(..., min_length=10, max_length=15)
