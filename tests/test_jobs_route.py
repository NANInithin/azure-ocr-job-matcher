import json
import os
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

MATCH_DIR = Path("data/match_results")


class TestGetSavedMatch:
    def test_returns_saved_match(self):
        doc_id = "test-doc-retrieval"
        job_id = "test-job-retrieval"
        match_file = MATCH_DIR / f"{doc_id}__{job_id}.json"
        match_data = {
            "job_id": job_id,
            "document_id": doc_id,
            "score": 90,
            "decision": "strong_match",
            "status": "saved_profile_match_complete",
        }

        MATCH_DIR.mkdir(parents=True, exist_ok=True)
        match_file.write_text(json.dumps(match_data), encoding="utf-8")

        try:
            response = client.get(f"/jobs/{job_id}/match/{doc_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["score"] == 90
            assert data["decision"] == "strong_match"
        finally:
            match_file.unlink(missing_ok=True)

    def test_returns_404_when_no_match(self):
        response = client.get("/jobs/ghost-job-999/match/ghost-doc-999")
        assert response.status_code == 404
        assert "No saved match found" in response.json()["detail"]