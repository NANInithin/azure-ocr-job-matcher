from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_analyze_document_returns_shape(monkeypatch):
    class DummyDocIntel:
        def analyze_from_bytes(self, content, model_id=None):
            return {
                "model_id": "prebuilt-layout",
                "full_text": "Jane Doe\nPython\nAzure",
                "page_count": 1,
                "raw_dict": {"content": "Jane Doe\nPython\nAzure"},
            }

    monkeypatch.setattr("app.api.routes.documents.DocumentIntelligenceService", lambda: DummyDocIntel())

    files = {"file": ("resume.txt", BytesIO(b"Jane Doe\nPython\nAzure"), "text/plain")}
    response = client.post("/documents/analyze", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "resume.txt"
    assert body["content_type"] == "text/plain"
    assert body["model_id"] == "prebuilt-layout"
    assert body["page_count"] == 1
    assert "Jane Doe" in body["full_text"]


def test_analyze_and_save_writes_files(monkeypatch):
    class DummyDocIntel:
        def analyze_from_bytes(self, content, model_id=None):
            return {
                "model_id": "prebuilt-layout",
                "full_text": "Jane Doe\nPython\nAzure",
                "page_count": 1,
                "raw_dict": {"content": "Jane Doe\nPython\nAzure"},
            }

    monkeypatch.setattr("app.api.routes.documents.DocumentIntelligenceService", lambda: DummyDocIntel())

    files = {"file": ("resume.txt", BytesIO(b"Jane Doe\nPython\nAzure"), "text/plain")}
    response = client.post("/documents/analyze-and-save", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "analyzed_and_saved"

    json_path = Path(body["saved_files"]["json_path"])
    text_path = Path(body["saved_files"]["text_path"])
    metadata_path = Path(body["saved_files"]["metadata_path"])

    assert json_path.exists()
    assert text_path.exists()
    assert metadata_path.exists()
    assert json_path.read_text(encoding="utf-8")
    assert text_path.read_text(encoding="utf-8") == "Jane Doe\nPython\nAzure"


def test_extract_candidate_profile_from_saved_text(monkeypatch):
    class DummyDocIntel:
        def analyze_from_bytes(self, content, model_id=None):
            return {
                "model_id": "prebuilt-layout",
                "full_text": "Jane Doe\nEmail: jane@example.com\nPython Azure Docker",
                "page_count": 1,
                "raw_dict": {"content": "Jane Doe\nEmail: jane@example.com\nPython Azure Docker"},
            }

    monkeypatch.setattr("app.api.routes.documents.DocumentIntelligenceService", lambda: DummyDocIntel())

    files = {
        "file": (
            "resume.txt",
            BytesIO(b"Jane Doe\nEmail: jane@example.com\nPython Azure Docker"),
            "text/plain",
        )
    }
    response = client.post("/documents/analyze-and-save", files=files)
    assert response.status_code == 200
    document_id = response.json()["document_id"]

    profile_response = client.post(f"/documents/{document_id}/extract-profile")
    assert profile_response.status_code == 200
    profile = profile_response.json()

    assert profile["document_id"] == document_id
    assert profile["profile"]["email"] == "jane@example.com"
    assert "python" in profile["profile"]["skills"]