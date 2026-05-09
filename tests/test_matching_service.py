from app.services.matching_service import MatchingService


def test_match_candidate_to_job_strong_match_with_evidence():
    profile = {
        "name": "Nithin Sai Kumar Kopparapu",
        "skills": ["python", "pytorch", "opencv", "docker", "computer vision", "cuda", "kubernetes", "tensorflow"],
        "linkedin": "linkedin.com/in/naninithin",
        "github": "github.com/NANNithin",
        "portfolio": None,
    }

    candidate_text = """
    Nithin Sai Kumar Kopparapu
    Skills: Python, PyTorch, OpenCV, Docker, Computer Vision, TensorFlow, CUDA, Kubernetes
    """

    job = {
        "title": "Computer Vision Engineer",
        "required_skills": ["python", "pytorch", "opencv", "docker", "computer vision"],
        "preferred_skills": ["cuda", "kubernetes", "tensorflow"],
    }

    service = MatchingService()
    result = service.match_candidate_to_job(profile, job, candidate_text=candidate_text)

    assert result["decision"] == "strong_match"
    assert result["score"] >= 90
    assert result["missing_required_skills"] == []
    assert "python" in result["matched_required_skills"]
    assert "cuda" in result["matched_preferred_skills"]

    assert "evidence" in result
    assert "python" in result["evidence"]
    assert "Skills:" in result["evidence"]["python"]

    assert "notes" in result
    assert any("matches all required skills" in note.lower() for note in result["notes"])


def test_match_candidate_to_job_weak_match_with_notes():
    profile = {
        "name": "Candidate A",
        "skills": ["excel", "communication"],
        "linkedin": None,
        "github": None,
        "portfolio": None,
    }

    candidate_text = """
    Candidate A
    Skills: Excel, Communication
    """

    job = {
        "title": "Computer Vision Engineer",
        "required_skills": ["python", "pytorch", "opencv"],
        "preferred_skills": ["docker"],
    }

    service = MatchingService()
    result = service.match_candidate_to_job(profile, job, candidate_text=candidate_text)

    assert result["decision"] == "weak_match"
    assert len(result["matched_required_skills"]) == 0
    assert "python" in result["missing_required_skills"]

    assert "evidence" in result
    assert result["evidence"] == {}

    assert "notes" in result
    assert any("missing" in note.lower() for note in result["notes"])

def test_match_candidate_to_job_moderate_match_when_one_required_skill_missing():
    profile = {
        "name": "Candidate B",
        "skills": ["python", "pytorch", "docker", "cuda"],
    }

    job = {
        "title": "Computer Vision Engineer",
        "required_skills": ["python", "pytorch", "opencv"],
        "preferred_skills": ["docker", "cuda"],
    }

    service = MatchingService()
    result = service.match_candidate_to_job(profile, job, candidate_text=None)

    assert result["decision"] == "moderate_match"
    assert result["score"] >= 60
    assert "opencv" in result["missing_required_skills"]
    assert "docker" in result["matched_preferred_skills"]
    assert result["evidence"] == {}
    assert any("missing" in note.lower() for note in result["notes"])


def test_match_candidate_to_job_strong_match_without_preferred_skills():
    profile = {
        "name": "Candidate C",
        "skills": ["python", "pytorch", "opencv"],
    }

    job = {
        "title": "Computer Vision Engineer",
        "required_skills": ["python", "pytorch", "opencv"],
        "preferred_skills": [],
    }

    service = MatchingService()
    result = service.match_candidate_to_job(profile, job, candidate_text=None)

    assert result["decision"] == "moderate_match"
    assert result["score"] == 80
    assert result["missing_required_skills"] == []
    assert result["matched_preferred_skills"] == []


def test_match_candidate_to_job_no_required_skills_uses_preferred_only():
    profile = {
        "name": "Candidate D",
        "skills": ["docker", "azure"],
    }

    job = {
        "title": "ML Platform Engineer",
        "required_skills": [],
        "preferred_skills": ["docker", "azure", "kubernetes"],
    }

    service = MatchingService()
    result = service.match_candidate_to_job(profile, job, candidate_text=None)

    assert result["score"] == 13
    assert result["decision"] == "weak_match"
    assert result["matched_required_skills"] == []
    assert sorted(result["matched_preferred_skills"]) == ["azure", "docker"]