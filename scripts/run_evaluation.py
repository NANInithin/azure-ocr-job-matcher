import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.services.candidate_profile_service import CandidateProfileService
from app.services.job_profile_service import JobProfileService
from app.services.matching_service import MatchingService

BASE = ROOT / "data" / "evaluation"
CANDIDATES_DIR = BASE / "candidates"
JOBS_DIR = BASE / "jobs"
MATCHING_DIR = BASE / "matching"

candidate_service = CandidateProfileService()
job_service = JobProfileService()
matching_service = MatchingService()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_candidates():
    results = []
    for expected_path in sorted(CANDIDATES_DIR.glob("*_expected.json")):
        sample_id = expected_path.stem.replace("_expected", "")
        text_path = CANDIDATES_DIR / f"{sample_id}.txt"
        expected = load_json(expected_path)
        predicted = candidate_service.extract_profile(text_path.read_text(encoding="utf-8"))

        checks = {
            "name": predicted.get("name") == expected.get("name"),
            "email": predicted.get("email") == expected.get("email"),
            "phone_contains": expected.get("phone_contains") is None or expected.get("phone_contains") in (predicted.get("phone") or ""),
            "linkedin_contains": expected.get("linkedin_contains") is None or expected.get("linkedin_contains") in (predicted.get("linkedin") or ""),
            "github_contains": expected.get("github_contains") is None or expected.get("github_contains") in (predicted.get("github") or ""),
            "skills_subset": set(expected.get("skills_expected", [])).issubset(set(predicted.get("skills", []))),
        }
        results.append((sample_id, checks))
    return results


def evaluate_jobs():
    results = []
    for expected_path in sorted(JOBS_DIR.glob("*_expected.json")):
        sample_id = expected_path.stem.replace("_expected", "")
        text_path = JOBS_DIR / f"{sample_id}.txt"
        expected = load_json(expected_path)
        predicted = job_service.parse_job_text(text_path.read_text(encoding="utf-8"))

        checks = {
            "title": predicted.get("title") == expected.get("title"),
            "location": predicted.get("location") == expected.get("location"),
            "minimum_years_experience": predicted.get("minimum_years_experience") == expected.get("minimum_years_experience"),
            "required_skills": set(expected.get("required_skills", [])) == set(predicted.get("required_skills", [])),
            "preferred_skills": set(expected.get("preferred_skills", [])) == set(predicted.get("preferred_skills", [])),
        }
        results.append((sample_id, checks))
    return results


def evaluate_matching():
    results = []
    for case_path in sorted(MATCHING_DIR.glob("match_case_*.json")):
        case = load_json(case_path)

        candidate_text = (CANDIDATES_DIR / case["candidate_file"]).read_text(encoding="utf-8")
        job_text = (JOBS_DIR / case["job_file"]).read_text(encoding="utf-8")

        candidate_profile = candidate_service.extract_profile(candidate_text)
        job_profile = job_service.parse_job_text(job_text)
        predicted = matching_service.match_candidate_to_job(
            candidate_profile, job_profile, candidate_text=candidate_text
        )

        checks = {
            "decision": predicted.get("decision") == case.get("expected_decision"),
            "required_skills_present": set(case.get("expected_required_skills_present", [])).issubset(
                set(predicted.get("matched_required_skills", []))
            ),
            "evidence_present": bool(predicted.get("evidence", {})),
            "notes_present": bool(predicted.get("notes", [])),
            "matched_required_skills_nonempty": bool(predicted.get("matched_required_skills", [])),
        }
        results.append((case_path.stem, checks))
    return results

def summarize(results, label):
    print(f"\n=== {label} ===")
    total = 0
    passed = 0
    for sample_id, checks in results:
        ok = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        total += total_checks
        passed += ok
        status = "PASS" if ok == total_checks else "PARTIAL"
        print(f"{sample_id}: {status} ({ok}/{total_checks}) -> {checks}")
    print(f"{label} summary: {passed}/{total} checks passed")


if __name__ == "__main__":
    summarize(evaluate_candidates(), "Candidate Extraction")
    summarize(evaluate_jobs(), "Job Parsing")
    summarize(evaluate_matching(), "Matching")
