from pathlib import Path
from uuid import uuid4
import json

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.services.blob_service import BlobStorageService
from app.services.document_intelligence_service import DocumentIntelligenceService
from app.services.candidate_profile_service import CandidateProfileService
from app.schemas.matching import JobRequirements
from app.services.matching_service import MatchingService

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/plain",
}

@router.get("/ping")
def ping_documents():
    return {"message": "documents route ready"}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    original_name = file.filename or "unknown"
    extension = Path(original_name).suffix
    stored_name = f"{uuid4()}{extension}"

    content = await file.read()

    blob_service = BlobStorageService()
    blob_url = blob_service.upload_file(
        blob_name=stored_name,
        data=content,
        content_type=file.content_type,
    )

    return {
        "original_filename": original_name,
        "stored_filename": stored_name,
        "content_type": file.content_type,
        "size_bytes": len(content),
        "blob_url": blob_url,
        "container": blob_service.container_name,
        "status": "uploaded"
    }


@router.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    content = await file.read()

    docintel_service = DocumentIntelligenceService()
    result = docintel_service.analyze_read_from_bytes(content)

    full_text = result.content if hasattr(result, "content") else ""

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "model_id": result.model_id,
        "full_text": full_text[:4000]
    }

@router.post("/analyze-and-save")
async def analyze_and_save_document(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    original_name = file.filename or "unknown"
    extension = Path(original_name).suffix
    document_id = str(uuid4())

    content = await file.read()

    docintel_service = DocumentIntelligenceService()
    analysis = docintel_service.analyze_read_from_bytes(content)

    output_dir = Path("data/ocr_outputs") / document_id
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "result.json"
    text_path = output_dir / "text.txt"
    metadata_path = output_dir / "metadata.json"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(analysis["raw_dict"], f, ensure_ascii=False, indent=2)

    text_path.write_text(analysis["full_text"], encoding="utf-8")

    metadata = {
        "document_id": document_id,
        "original_filename": original_name,
        "content_type": file.content_type,
        "model_id": analysis["model_id"],
        "page_count": analysis["page_count"],
        "text_char_count": len(analysis["full_text"]),
        "json_path": str(json_path),
        "text_path": str(text_path),
    }

    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return {
        "document_id": document_id,
        "original_filename": original_name,
        "model_id": analysis["model_id"],
        "page_count": analysis["page_count"],
        "text_char_count": len(analysis["full_text"]),
        "saved_files": {
            "json_path": str(json_path),
            "text_path": str(text_path),
            "metadata_path": str(metadata_path),
        },
        "preview_text": analysis["full_text"][:1000],
        "status": "analyzed_and_saved",
    }

@router.post("/{document_id}/extract-profile")
async def extract_candidate_profile(document_id: str):
    output_dir = Path("data/ocr_outputs") / document_id
    text_path = output_dir / "text.txt"
    profile_path = output_dir / "candidate_profile.json"

    if not text_path.exists():
        raise HTTPException(status_code=404, detail=f"OCR text not found for document_id={document_id}")

    text = text_path.read_text(encoding="utf-8")

    profile_service = CandidateProfileService()
    profile = profile_service.extract_profile(text)

    profile_payload = {
        "document_id": document_id,
        "profile": profile,
        "source_text_path": str(text_path),
        "profile_path": str(profile_path),
        "status": "profile_extracted"
    }

    with profile_path.open("w", encoding="utf-8") as f:
        json.dump(profile_payload, f, ensure_ascii=False, indent=2)

    return profile_payload

@router.post("/{document_id}/match")
async def match_candidate_to_job(document_id: str, job: JobRequirements):
    output_dir = Path("data/ocr_outputs") / document_id
    profile_path = output_dir / "candidate_profile.json"

    if not profile_path.exists():
        raise HTTPException(status_code=404, detail=f"Candidate profile not found for document_id={document_id}")

    profile_payload = json.loads(profile_path.read_text(encoding="utf-8"))
    profile = profile_payload.get("profile", {})

    matching_service = MatchingService()
    match_result = matching_service.match_candidate_to_job(profile, job.model_dump())

    return {
        "document_id": document_id,
        "job_title": job.title,
        "candidate_name": profile.get("name"),
        **match_result,
    }