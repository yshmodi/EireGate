from pydantic import BaseModel, Field, validator
from typing import List, Optional

class ContactInfo(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    linkedin: Optional[str] = None
    location: Optional[str] = None

class EducationEntry(BaseModel):
    degree: str
    field: str = ""
    institution: str
    year: str
    nfq_level: Optional[int] = Field(None, ge=7, le=10)

class ExperienceEntry(BaseModel):
    title: str
    company: str
    dates: str
    bullets: List[str] = Field(default_factory=list)

class SkillCategory(BaseModel):
    name: str
    items: List[str]

class Project(BaseModel):
    title: str
    description: str=""
    tech: List[str] = Field(default_factory=list)

class Resume(BaseModel):
    name: str
    contact: ContactInfo
    summary: str=""
    education: List[EducationEntry] = Field(min_length=1)
    experience: List[ExperienceEntry] = []
    skills: List[SkillCategory] = Field(min_length=1)
    projects: List[Project] = []
    certifications: List[dict] = []
    visa_notes: dict = Field(default_factory=dict)
