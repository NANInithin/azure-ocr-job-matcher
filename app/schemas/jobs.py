from pydantic import BaseModel, Field
from typing import List, Optional


class JobTextInput(BaseModel):
    job_text: str = Field(..., min_length=20, description="Raw job description text")


class JobProfile(BaseModel):
    job_id: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    minimum_years_experience: Optional[int] = None
    raw_job_text_path: str
    job_profile_path: str
    status: str