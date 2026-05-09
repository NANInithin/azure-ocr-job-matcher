import os
from fastapi import APIRouter, HTTPException
from typing import Any

router = APIRouter(prefix="/registry", tags=["registry"])

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
OCR_DIR = os.path.join(DATA_DIR, "ocr_outputs")
JOBS_DIR = os.path.join(DATA_DIR, "job_profiles")
MATCH_DIR = os.path.join(DATA_DIR, "match_results")


def _list_artifact_folders(base_dir: str) -> list[dict[str, Any]]:
    if not os.path.isdir(base_dir):
        return []
    entries = []
    for name in sorted(os.listdir(base_dir)):
        folder_path = os.path.join(base_dir, name)
        if not os.path.isdir(folder_path):
            continue
        files = sorted(os.listdir(folder_path))
        stat = os.stat(folder_path)
        entries.append({
            "id": name,
            "files": files,
            "file_count": len(files),
            "created_at": stat.st_ctime,
        })
    return entries


def _list_artifact_files(base_dir: str) -> list[dict[str, Any]]:
    if not os.path.isdir(base_dir):
        return []
    entries = []
    for name in sorted(os.listdir(base_dir)):
        file_path = os.path.join(base_dir, name)
        if not os.path.isfile(file_path):
            continue
        stat = os.stat(file_path)
        entries.append({
            "filename": name,
            "size_bytes": stat.st_size,
            "created_at": stat.st_ctime,
        })
    return entries


@router.get("/summary", summary="Summary count of all persisted artifacts")
def registry_summary() -> dict[str, Any]:
    docs = _list_artifact_folders(OCR_DIR)
    jobs = _list_artifact_folders(JOBS_DIR)
    matches = _list_artifact_files(MATCH_DIR)
    profiles_extracted = sum(
        1 for d in docs if "candidate_profile.json" in d["files"]
    )
    return {
        "total_documents": len(docs),
        "documents_with_profile": profiles_extracted,
        "total_jobs": len(jobs),
        "total_matches": len(matches),
    }


@router.get("/documents", summary="List all processed OCR document artifacts")
def list_documents() -> dict[str, Any]:
    entries = _list_artifact_folders(OCR_DIR)
    return {"total": len(entries), "documents": entries}


@router.get("/documents/{document_id}", summary="Get artifact details for a specific document")
def get_document_artifact(document_id: str) -> dict[str, Any]:
    folder = os.path.join(OCR_DIR, document_id)
    if not os.path.isdir(folder):
        raise HTTPException(status_code=404, detail=f"Document artifact '{document_id}' not found.")
    files = sorted(os.listdir(folder))
    stat = os.stat(folder)
    return {
        "id": document_id,
        "files": files,
        "file_count": len(files),
        "created_at": stat.st_ctime,
        "has_candidate_profile": "candidate_profile.json" in files,
    }


@router.get("/jobs", summary="List all saved job profile artifacts")
def list_jobs() -> dict[str, Any]:
    entries = _list_artifact_folders(JOBS_DIR)
    return {"total": len(entries), "jobs": entries}


@router.get("/jobs/{job_id}", summary="Get artifact details for a specific job profile")
def get_job_artifact(job_id: str) -> dict[str, Any]:
    folder = os.path.join(JOBS_DIR, job_id)
    if not os.path.isdir(folder):
        raise HTTPException(status_code=404, detail=f"Job profile artifact '{job_id}' not found.")
    files = sorted(os.listdir(folder))
    stat = os.stat(folder)
    return {"id": job_id, "files": files, "file_count": len(files), "created_at": stat.st_ctime}


@router.get("/matches", summary="List all saved match result artifacts")
def list_matches() -> dict[str, Any]:
    entries = _list_artifact_files(MATCH_DIR)
    return {"total": len(entries), "matches": entries}