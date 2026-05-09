from typing import List, Optional

from pydantic import BaseModel, Field


class JobRequirements(BaseModel):
    title: str = Field(..., description="Job title for the target role", examples=["Computer Vision Engineer"])
    company: Optional[str] = Field(default=None, description="Company name", examples=["Industrial Vision AI"])
    required_skills: List[str] = Field(
        default_factory=list,
        description="Skills that are mandatory for the role",
        examples=[["python", "pytorch", "opencv", "computer vision", "deep learning"]],
    )
    preferred_skills: List[str] = Field(
        default_factory=list,
        description="Skills that improve the candidate fit score",
        examples=[["azure", "docker", "kubernetes", "cuda", "tensorflow"]],
    )
    minimum_years_experience: Optional[int] = Field(
        default=None,
        description="Minimum years of experience expected",
        examples=[2],
    )
    location: Optional[str] = Field(
        default=None,
        description="Primary job location",
        examples=["France"],
    )
    remote_ok: Optional[bool] = Field(
        default=None,
        description="Whether remote work is acceptable",
        examples=[True],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Computer Vision Engineer",
                    "company": "Industrial Vision AI",
                    "required_skills": [
                        "python",
                        "pytorch",
                        "opencv",
                        "computer vision",
                        "deep learning"
                    ],
                    "preferred_skills": [
                        "azure",
                        "docker",
                        "kubernetes",
                        "cuda",
                        "tensorflow"
                    ],
                    "minimum_years_experience": 2,
                    "location": "France",
                    "remote_ok": True
                }
            ]
        }
    }


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