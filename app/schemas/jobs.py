from pydantic import BaseModel, Field
from typing import List, Optional


class JobTextInput(BaseModel):
    job_text: str = Field(
        ...,
        min_length=20,
        description="Raw job description text",
        examples=[
            "Computer Vision Engineer\nLocation: France\nWe are looking for a Computer Vision Engineer with 2+ years of experience. Required skills include Python, PyTorch, OpenCV, Docker, and computer vision. Preferred skills include Azure, Kubernetes, CUDA, and TensorFlow."
        ],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "job_text": "Computer Vision Engineer\nLocation: France\nWe are looking for a Computer Vision Engineer with 2+ years of experience. Required skills include Python, PyTorch, OpenCV, Docker, and computer vision. Preferred skills include Azure, Kubernetes, CUDA, and TensorFlow."
                }
            ]
        }
    }


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
    notes: List[str] = Field(default_factory=list)