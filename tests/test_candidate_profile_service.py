from app.services.candidate_profile_service import CandidateProfileService


def test_extract_candidate_profile_basic_fields():
    text = """
    Nithin Sai Kumar Kopparapu
    France · +33 0780789495 · naniknsk2002@gmail.com
    linkedin.com/in/naninithin · github.com/NANNithin

    Skills: Python, PyTorch, OpenCV, Docker, Computer Vision, TensorFlow
    """

    service = CandidateProfileService()
    profile = service.extract_profile(text)

    assert profile["name"] == "Nithin Sai Kumar Kopparapu"
    assert profile["email"] == "naniknsk2002@gmail.com"
    assert "+33" in profile["phone"]
    assert "linkedin.com" in profile["linkedin"]
    assert "github.com" in profile["github"]
    assert "python" in profile["skills"]
    assert "pytorch" in profile["skills"]
    assert "opencv" in profile["skills"]