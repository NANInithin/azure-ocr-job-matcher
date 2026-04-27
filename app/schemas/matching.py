from pydantic import BaseModel, Field
from typing import List, Optional


class JobRequirements(BaseModel):
    title: str
    company: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    minimum_years_experience: Optional[int] = None
    location: Optional[str] = None
    remote_ok: Optional[bool] = None


class MatchResult(BaseModel):
    document_id: str
    job_title: str
    candidate_name: Optional[str] = None
    matched_required_skills: List[str]
    missing_required_skills: List[str]
    matched_preferred_skills: List[str]
    score: float
    decision: str
    notes: List[str]