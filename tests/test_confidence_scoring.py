from app.services.candidate_profile_service import CandidateProfileService
from app.services.job_profile_service import JobProfileService

candidate_svc = CandidateProfileService()
job_svc = JobProfileService()


class TestCandidateConfidence:
    def test_confidence_keys_present(self):
        result = candidate_svc.extract_profile("Alice Smith\nalice@example.com\nPython Docker Azure")
        assert "field_confidence" in result
        assert set(result["field_confidence"].keys()) == {
            "name", "email", "phone", "linkedin", "github", "portfolio", "skills"
        }

    def test_email_found_gives_high_confidence(self):
        result = candidate_svc.extract_profile("Alice\nalice@example.com")
        assert result["field_confidence"]["email"] == 1.0

    def test_no_email_gives_zero_confidence(self):
        result = candidate_svc.extract_profile("Alice Smith\nNo contact info here")
        assert result["field_confidence"]["email"] == 0.0

    def test_name_with_email_boosts_confidence(self):
        result = candidate_svc.extract_profile("Alice Smith\nalice@example.com")
        assert result["field_confidence"]["name"] >= 0.7

    def test_many_skills_gives_high_confidence(self):
        result = candidate_svc.extract_profile(
            "python pytorch tensorflow docker kubernetes azure fastapi pandas numpy"
        )
        assert result["field_confidence"]["skills"] == 0.9

    def test_no_skills_gives_zero_confidence(self):
        result = candidate_svc.extract_profile("I love cooking and gardening")
        assert result["field_confidence"]["skills"] == 0.0

    def test_confidence_values_are_floats_in_range(self):
        result = candidate_svc.extract_profile("Alice\nalice@example.com\npython docker")
        for key, val in result["field_confidence"].items():
            assert isinstance(val, float), f"{key} confidence is not float"
            assert 0.0 <= val <= 1.0, f"{key} confidence {val} out of range"


class TestJobConfidence:
    def test_confidence_keys_present(self):
        job_text = "ML Engineer\nLocation: Berlin\nRequired: python docker\n3+ years of experience"
        result = job_svc.parse_job_text(job_text)
        assert "field_confidence" in result
        assert set(result["field_confidence"].keys()) == {
            "title", "company", "location", "required_skills",
            "preferred_skills", "minimum_years_experience"
        }

    def test_explicit_location_gives_high_confidence(self):
        result = job_svc.parse_job_text("ML Engineer\nLocation: Berlin\npython docker")
        assert result["field_confidence"]["location"] == 1.0

    def test_no_location_gives_zero_confidence(self):
        result = job_svc.parse_job_text("ML Engineer\npython docker machine learning")
        assert result["field_confidence"]["location"] == 0.0

    def test_years_experience_found_gives_high_confidence(self):
        result = job_svc.parse_job_text("ML Engineer\n3+ years of experience\npython docker")
        assert result["field_confidence"]["minimum_years_experience"] == 0.95

    def test_no_years_experience_gives_zero_confidence(self):
        result = job_svc.parse_job_text("ML Engineer\npython docker machine learning")
        assert result["field_confidence"]["minimum_years_experience"] == 0.0

    def test_fallback_skills_lowers_confidence(self):
        # No "required" section heading → fallback → lower confidence
        result = job_svc.parse_job_text(
            "ML Engineer\nskills: python docker machine learning deep learning"
        )
        assert result["field_confidence"]["required_skills"] <= 0.65

    def test_confidence_values_are_floats_in_range(self):
        result = job_svc.parse_job_text(
            "ML Engineer\nLocation: Berlin\nRequired:\npython docker\n3+ years of experience"
        )
        for key, val in result["field_confidence"].items():
            assert isinstance(val, float), f"{key} is not float"
            assert 0.0 <= val <= 1.0, f"{key} = {val} out of range"