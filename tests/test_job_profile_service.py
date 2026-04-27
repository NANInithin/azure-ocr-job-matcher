from app.services.job_profile_service import JobProfileService


def test_parse_job_text_required_and_preferred_skills():
    text = """
    Computer Vision Engineer
    Location: France

    We are looking for a Computer Vision Engineer with 2+ years of experience.
    Required skills include Python, PyTorch, OpenCV, Docker, and computer vision.
    Preferred skills include Azure, Kubernetes, CUDA, and TensorFlow.
    """

    service = JobProfileService()
    job = service.parse_job_text(text)

    assert job["title"] == "Computer Vision Engineer"
    assert job["location"] == "France"
    assert job["minimum_years_experience"] == 2

    assert "python" in job["required_skills"]
    assert "pytorch" in job["required_skills"]
    assert "opencv" in job["required_skills"]
    assert "docker" in job["required_skills"]
    assert "computer vision" in job["required_skills"]

    assert "azure" in job["preferred_skills"]
    assert "kubernetes" in job["preferred_skills"]
    assert "cuda" in job["preferred_skills"]
    assert "tensorflow" in job["preferred_skills"]

    assert "azure" not in job["required_skills"]