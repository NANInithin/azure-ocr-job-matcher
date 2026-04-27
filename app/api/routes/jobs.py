import json
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter

from app.schemas.jobs import JobTextInput
from app.services.job_profile_service import JobProfileService
from fastapi import APIRouter, HTTPException
from app.services.matching_service import MatchingService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/parse")
async def parse_job_description(payload: JobTextInput):
    job_id = str(uuid4())
    output_dir = Path("data/job_profiles") / job_id
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_text_path = output_dir / "raw_job_text.txt"
    profile_path = output_dir / "job_profile.json"

    raw_text_path.write_text(payload.job_text, encoding="utf-8")

    job_service = JobProfileService()
    parsed = job_service.parse_job_text(payload.job_text)

    job_profile = {
        "job_id": job_id,
        **parsed,
        "raw_job_text_path": str(raw_text_path),
        "job_profile_path": str(profile_path),
        "status": "job_profile_created",
    }

    with profile_path.open("w", encoding="utf-8") as f:
        json.dump(job_profile, f, ensure_ascii=False, indent=2)

    return job_profile

@router.post("/{job_id}/match/{document_id}")
async def match_saved_job_to_candidate(job_id: str, document_id: str):
    job_profile_path = Path("data/job_profiles") / job_id / "job_profile.json"
    candidate_profile_path = Path("data/ocr_outputs") / document_id / "candidate_profile.json"
    match_output_dir = Path("data/match_results")
    match_output_dir.mkdir(parents=True, exist_ok=True)

    if not job_profile_path.exists():
        raise HTTPException(status_code=404, detail=f"Job profile not found for job_id={job_id}")

    if not candidate_profile_path.exists():
        raise HTTPException(status_code=404, detail=f"Candidate profile not found for document_id={document_id}")

    job_profile = json.loads(job_profile_path.read_text(encoding="utf-8"))
    candidate_payload = json.loads(candidate_profile_path.read_text(encoding="utf-8"))
    candidate_profile = candidate_payload.get("profile", {})

    matching_service = MatchingService()
    match_result = matching_service.match_candidate_to_job(candidate_profile, job_profile)

    output = {
        "job_id": job_id,
        "document_id": document_id,
        "job_title": job_profile.get("title"),
        "candidate_name": candidate_profile.get("name"),
        **match_result,
        "status": "saved_profile_match_complete"
    }

    match_file = match_output_dir / f"{document_id}__{job_id}.json"
    with match_file.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    output["match_result_path"] = str(match_file)
    return output