"""Evaluation harness for the OCR-to-profile-to-match pipeline.

Usage:
    python scripts/run_evaluation.py           # run all checks, print report
    python scripts/run_evaluation.py --strict  # exit 1 if any check fails (CI mode)

Checks:
    - Candidate field extraction (name, email, phone, linkedin, github, skills)
    - Candidate field confidence thresholds (all key fields >= 0.5)
    - Job description parsing (title, location, years, required/preferred skills)
    - Job field confidence thresholds (all key fields >= 0.5)
    - End-to-end matching decisions, evidence, and notes

Exit codes:
    0  all checks passed
    1  one or more checks failed (only when --strict is set)
"""

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

CANDIDATE_CONFIDENCE_THRESHOLD = 0.5
JOB_CONFIDENCE_THRESHOLD = 0.5
CANDIDATE_CONFIDENCE_FIELDS = ["name", "email", "phone", "skills"]
JOB_CONFIDENCE_FIELDS = ["title", "location", "required_skills"]

candidate_service = CandidateProfileService()
job_service = JobProfileService()
matching_service = MatchingService()

STRICT = "--strict" in sys.argv


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _confidence_checks(field_confidence: dict, fields: list, threshold: float, expected: dict) -> dict:
    """Only check confidence for fields that were actually expected in this fixture."""
    return {
        f"confidence_{f}": field_confidence.get(f, 0.0) >= threshold
        for f in fields
        if f in field_confidence and expected.get(f) is not None
    }


# ---------------------------------------------------------------------------
# Candidate extraction
# ---------------------------------------------------------------------------

def evaluate_candidates():
    results = []
    for expected_path in sorted(CANDIDATES_DIR.glob("*_expected.json")):
        sample_id = expected_path.stem.replace("_expected", "")
        text_path = CANDIDATES_DIR / f"{sample_id}.txt"
        expected = load_json(expected_path)
        predicted = candidate_service.extract_profile(text_path.read_text(encoding="utf-8"))
        field_confidence = predicted.get("field_confidence", {})

        checks = {
            "name": predicted.get("name") == expected.get("name"),
            "email": predicted.get("email") == expected.get("email"),
            "phone_contains": (
                expected.get("phone_contains") is None
                or expected.get("phone_contains") in (predicted.get("phone") or "")
            ),
            "linkedin_contains": (
                expected.get("linkedin_contains") is None
                or expected.get("linkedin_contains") in (predicted.get("linkedin") or "")
            ),
            "github_contains": (
                expected.get("github_contains") is None
                or expected.get("github_contains") in (predicted.get("github") or "")
            ),
            "skills_subset": set(expected.get("skills_expected", [])).issubset(
                set(predicted.get("skills", []))
            ),
        }

        if field_confidence:
            checks.update(
                _confidence_checks(field_confidence, CANDIDATE_CONFIDENCE_FIELDS, CANDIDATE_CONFIDENCE_THRESHOLD, expected)
            )

        results.append((sample_id, checks))
    return results


# ---------------------------------------------------------------------------
# Job parsing
# ---------------------------------------------------------------------------

def evaluate_jobs():
    results = []
    for expected_path in sorted(JOBS_DIR.glob("*_expected.json")):
        sample_id = expected_path.stem.replace("_expected", "")
        text_path = JOBS_DIR / f"{sample_id}.txt"
        expected = load_json(expected_path)
        predicted = job_service.parse_job_text(text_path.read_text(encoding="utf-8"))
        field_confidence = predicted.get("field_confidence", {})

        checks = {
            "title": predicted.get("title") == expected.get("title"),
            "location": predicted.get("location") == expected.get("location"),
            "minimum_years_experience": (
                predicted.get("minimum_years_experience") == expected.get("minimum_years_experience")
            ),
            "required_skills": (
                set(expected.get("required_skills", [])) == set(predicted.get("required_skills", []))
            ),
            "preferred_skills": (
                set(expected.get("preferred_skills", [])) == set(predicted.get("preferred_skills", []))
            ),
        }

        if field_confidence:
            checks.update(
                _confidence_checks(field_confidence, JOB_CONFIDENCE_FIELDS, JOB_CONFIDENCE_THRESHOLD, expected)
            )

        results.append((sample_id, checks))
    return results


# ---------------------------------------------------------------------------
# End-to-end matching
# ---------------------------------------------------------------------------

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

        expected_score_min = case.get("expected_score_min")
        expected_score_max = case.get("expected_score_max")
        actual_score = predicted.get("score", 0)

        checks = {
            "decision": predicted.get("decision") == case.get("expected_decision"),
            "required_skills_present": set(case.get("expected_required_skills_present", [])).issubset(
                set(predicted.get("matched_required_skills", []))
            ),
            "evidence_present": bool(predicted.get("evidence", {})),
            "notes_present": bool(predicted.get("notes", [])),
            "matched_required_skills_nonempty": bool(predicted.get("matched_required_skills", [])),
        }

        if expected_score_min is not None:
            checks["score_min"] = actual_score >= expected_score_min
        if expected_score_max is not None:
            checks["score_max"] = actual_score <= expected_score_max

        results.append((case_path.stem, checks))
    return results


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def summarize(results: list, label: str) -> tuple:
    print(f"\n{'=' * 55}")
    print(f"  {label}")
    print(f"{'=' * 55}")
    total = 0
    passed = 0
    for sample_id, checks in results:
        ok = sum(1 for v in checks.values() if v)
        total_checks = len(checks)
        total += total_checks
        passed += ok
        icon = "PASS" if ok == total_checks else "FAIL"
        print(f"  [{icon}] {sample_id}: {ok}/{total_checks}")
        if ok < total_checks:
            for check_name, result in checks.items():
                if not result:
                    print(f"         x {check_name}")
    print(f"\n  Section total: {passed}/{total}")
    return passed, total


def print_final_report(sections: list) -> bool:
    grand_passed = sum(p for _, p, _ in sections)
    grand_total = sum(t for _, _, t in sections)
    all_passed = grand_passed == grand_total

    print(f"\n{'=' * 55}")
    print(f"  EVALUATION SUMMARY")
    print(f"{'=' * 55}")
    for label, p, t in sections:
        icon = "OK" if p == t else "!!"
        print(f"  [{icon}] {label}: {p}/{t}")
    print(f"{'=' * 55}")
    print(f"  TOTAL: {grand_passed}/{grand_total} checks passed")
    status = "ALL CHECKS PASSED" if all_passed else "SOME CHECKS FAILED"
    print(f"  STATUS: {status}")
    print(f"{'=' * 55}\n")
    return all_passed


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sections = []

    r = evaluate_candidates()
    p, t = summarize(r, "Candidate Extraction")
    sections.append(("Candidate Extraction", p, t))

    r = evaluate_jobs()
    p, t = summarize(r, "Job Parsing")
    sections.append(("Job Parsing", p, t))

    r = evaluate_matching()
    p, t = summarize(r, "Matching & Explainability")
    sections.append(("Matching & Explainability", p, t))

    all_passed = print_final_report(sections)

    if STRICT and not all_passed:
        sys.exit(1)