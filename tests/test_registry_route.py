import os
import json
import tempfile
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


def make_artifact_folder(base: str, artifact_id: str, files: dict) -> None:
    folder = os.path.join(base, artifact_id)
    os.makedirs(folder, exist_ok=True)
    for filename, content in files.items():
        with open(os.path.join(folder, filename), "w") as f:
            json.dump(content, f) if isinstance(content, dict) else f.write(content)


class TestRegistrySummary:
    def test_summary_returns_counts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ocr_dir = os.path.join(tmpdir, "ocr_outputs")
            jobs_dir = os.path.join(tmpdir, "job_profiles")
            match_dir = os.path.join(tmpdir, "match_results")
            os.makedirs(ocr_dir); os.makedirs(jobs_dir); os.makedirs(match_dir)

            make_artifact_folder(ocr_dir, "doc-001", {
                "result.json": {}, "text.txt": "x",
                "metadata.json": {}, "candidate_profile.json": {"name": "Alice"},
            })
            make_artifact_folder(ocr_dir, "doc-002", {
                "result.json": {}, "text.txt": "y", "metadata.json": {},
            })
            make_artifact_folder(jobs_dir, "job-001", {
                "job_profile.json": {"title": "Engineer"}, "raw_job_text.txt": "text",
            })
            with open(os.path.join(match_dir, "doc-001__job-001.json"), "w") as f:
                json.dump({"score": 90}, f)

            with patch("app.api.routes.registry.OCR_DIR", ocr_dir), \
                 patch("app.api.routes.registry.JOBS_DIR", jobs_dir), \
                 patch("app.api.routes.registry.MATCH_DIR", match_dir):
                response = client.get("/registry/summary")
                assert response.status_code == 200
                data = response.json()
                assert data["total_documents"] == 2
                assert data["documents_with_profile"] == 1
                assert data["total_jobs"] == 1
                assert data["total_matches"] == 1


class TestListDocuments:
    def test_returns_all_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ocr_dir = os.path.join(tmpdir, "ocr_outputs")
            os.makedirs(ocr_dir)
            make_artifact_folder(ocr_dir, "doc-aaa", {"result.json": {}, "text.txt": "x"})
            make_artifact_folder(ocr_dir, "doc-bbb", {"result.json": {}, "candidate_profile.json": {}})
            with patch("app.api.routes.registry.OCR_DIR", ocr_dir):
                response = client.get("/registry/documents")
                assert response.status_code == 200
                data = response.json()
                assert data["total"] == 2
                assert {d["id"] for d in data["documents"]} == {"doc-aaa", "doc-bbb"}

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ocr_dir = os.path.join(tmpdir, "ocr_outputs")
            os.makedirs(ocr_dir)
            with patch("app.api.routes.registry.OCR_DIR", ocr_dir):
                response = client.get("/registry/documents")
                assert response.status_code == 200
                assert response.json()["total"] == 0


class TestGetDocumentArtifact:
    def test_found_with_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ocr_dir = os.path.join(tmpdir, "ocr_outputs")
            os.makedirs(ocr_dir)
            make_artifact_folder(ocr_dir, "doc-xyz", {
                "result.json": {}, "text.txt": "t", "candidate_profile.json": {},
            })
            with patch("app.api.routes.registry.OCR_DIR", ocr_dir):
                response = client.get("/registry/documents/doc-xyz")
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == "doc-xyz"
                assert data["has_candidate_profile"] is True
                assert data["file_count"] == 3

    def test_missing_returns_404(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ocr_dir = os.path.join(tmpdir, "ocr_outputs")
            os.makedirs(ocr_dir)
            with patch("app.api.routes.registry.OCR_DIR", ocr_dir):
                response = client.get("/registry/documents/ghost-id")
                assert response.status_code == 404


class TestListJobs:
    def test_returns_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            jobs_dir = os.path.join(tmpdir, "job_profiles")
            os.makedirs(jobs_dir)
            make_artifact_folder(jobs_dir, "job-111", {
                "job_profile.json": {"title": "ML Engineer"}, "raw_job_text.txt": "text",
            })
            with patch("app.api.routes.registry.JOBS_DIR", jobs_dir):
                response = client.get("/registry/jobs")
                assert response.status_code == 200
                data = response.json()
                assert data["total"] == 1
                assert data["jobs"][0]["id"] == "job-111"


class TestListMatches:
    def test_returns_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            match_dir = os.path.join(tmpdir, "match_results")
            os.makedirs(match_dir)
            with open(os.path.join(match_dir, "doc-001__job-001.json"), "w") as f:
                json.dump({"score": 85}, f)
            with patch("app.api.routes.registry.MATCH_DIR", match_dir):
                response = client.get("/registry/matches")
                assert response.status_code == 200
                data = response.json()
                assert data["total"] == 1
                assert data["matches"][0]["filename"] == "doc-001__job-001.json"

    def test_empty_returns_zero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            match_dir = os.path.join(tmpdir, "match_results")
            os.makedirs(match_dir)
            with patch("app.api.routes.registry.MATCH_DIR", match_dir):
                response = client.get("/registry/matches")
                assert response.status_code == 200
                assert response.json()["total"] == 0