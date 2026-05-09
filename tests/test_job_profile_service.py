from app.services.job_profile_service import JobProfileService


def test_parse_job_text_extracts_required_and_preferred_sections():
    service = JobProfileService()

    job_text = """
Computer Vision Engineer
Company: Industrial Vision AI
Location: France

Required Qualifications:
Python, PyTorch, OpenCV, Docker, Computer Vision, Deep Learning
Minimum of 2 years experience

Preferred Qualifications:
Azure, Kubernetes, CUDA, TensorFlow
"""

    result = service.parse_job_text(job_text)

    assert result["title"] == "Computer Vision Engineer"
    assert result["company"] == "Industrial Vision AI"
    assert result["location"] == "France"
    assert result["minimum_years_experience"] == 2

    assert "python" in result["required_skills"]
    assert "pytorch" in result["required_skills"]
    assert "opencv" in result["required_skills"]
    assert "docker" in result["required_skills"]
    assert "computer vision" in result["required_skills"]
    assert "deep learning" in result["required_skills"]

    assert "azure" in result["preferred_skills"]
    assert "kubernetes" in result["preferred_skills"]
    assert "cuda" in result["preferred_skills"]
    assert "tensorflow" in result["preferred_skills"]

    assert not set(result["required_skills"]) & set(result["preferred_skills"])

def test_parse_job_text_falls_back_to_general_skill_extraction():
    service = JobProfileService()

    job_text = """
About the job
Computer Vision/AI Engineer

Amsterdam, Netherlands

Strong Python skills and hands on use of PyTorch.
Practical experience with computer vision fundamentals, including object detection or image processing.
Exposure to cloud platforms such as AWS or GCP is beneficial.
Any exposure to image focused generative AI is a bonus.
"""

    result = service.parse_job_text(job_text)

    assert result["title"] == "Computer Vision/AI Engineer"
    assert "pytorch" in result["required_skills"]
    assert "computer vision" in result["required_skills"]

def test_parse_job_text_adds_notes_for_ambiguous_input():
    service = JobProfileService()

    job_text = """
We are hiring an AI engineer to work on vision models.
Hands-on experience with PyTorch and computer vision is valuable.
Cloud exposure is a plus.
"""

    result = service.parse_job_text(job_text)

    assert isinstance(result["notes"], list)
    assert len(result["notes"]) > 0
    assert any("Location not found" in note for note in result["notes"])
    assert any("Minimum years of experience not found" in note for note in result["notes"])