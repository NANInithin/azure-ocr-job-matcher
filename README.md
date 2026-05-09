# Azure Job Application Selector

A production-style OCR and document intelligence backend that analyzes candidate application documents, extracts structured profiles, parses job descriptions, and computes explainable candidate-job match results using Azure services and FastAPI.

## Why this project

This project is being built as an 8-week portfolio system focused on recruiter-visible engineering depth in OCR, backend orchestration, structured extraction, reproducible artifacts, and explainable matching workflows. The backend follows a modular FastAPI structure with routers, schemas, and service layers, which aligns with common FastAPI organization patterns for larger applications.

## Current status

The current implementation supports candidate OCR processing, candidate profile extraction, job description parsing, saved-profile matching, artifact registry endpoints, field confidence scoring on all extracted outputs, service-layer unit tests, route-level tests, schema-backed Swagger examples, parser notes for ambiguous job descriptions, and edge-case matcher validation. The project includes reproducible saved artifacts for OCR outputs, job profiles, and match results, which makes debugging and evaluation easier in document intelligence systems.

## Architecture

```mermaid
flowchart TD
    A[Candidate Resume PDF or Image] --> B[POST /documents/analyze-and-save]
    B --> C[Azure Document Intelligence OCR]
    C --> D[OCR JSON plus text plus metadata]

    D --> E[POST /documents/document_id/extract-profile]
    E --> F[Candidate Profile JSON with confidence scores]

    G[Raw Job Description Text] --> H[POST /jobs/parse]
    H --> I[Job Profile JSON with confidence scores]

    F --> J[POST /jobs/job_id/match/document_id]
    I --> J
    J --> K[Match Result JSON plus evidence plus notes]

    K --> L[GET /registry/summary]
    L --> M[Artifact counts across documents, jobs, matches]
```

The backend is organized so document ingestion, parsing, and matching logic remain separated instead of being coupled inside one script, which makes later extension into evaluation, async processing, and retrieval easier.

## Project structure

```text
.
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes/
│   │       ├── health.py
│   │       ├── documents.py
│   │       ├── jobs.py
│   │       └── registry.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── models/
│   ├── schemas/
│   │   ├── jobs.py
│   │   └── matching.py
│   └── services/
│       ├── blob_service.py
│       ├── candidate_profile_service.py
│       ├── document_intelligence_service.py
│       ├── job_profile_service.py
│       └── matching_service.py
├── data/
│   ├── evaluation/
│   │   ├── candidates/
│   │   ├── jobs/
│   │   └── matching/
│   ├── job_profiles/         <- gitignored, created at runtime
│   ├── match_results/        <- gitignored, created at runtime
│   ├── ocr_outputs/          <- gitignored, created at runtime
│   └── uploads/              <- gitignored, created at runtime
├── scripts/
│   └── run_evaluation.py
├── tests/
│   ├── conftest.py
│   ├── test_candidate_profile_service.py
│   ├── test_confidence_scoring.py
│   ├── test_documents_route.py
│   ├── test_job_profile_service.py
│   ├── test_matching_service.py
│   └── test_registry_route.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Features

- Upload candidate documents and process them with Azure Document Intelligence OCR.
- Save OCR artifacts as raw JSON, plain text, and metadata for each document.
- Extract structured candidate profile fields from OCR output using deterministic parsing rules.
- Attach field-level confidence scores to every extracted candidate profile field.
- Parse raw job descriptions into title, location, skills, years of experience, and parser notes for ambiguous inputs.
- Attach field-level confidence scores to every extracted job profile field.
- Match saved candidate profiles against saved job profiles with transparent scoring, evidence snippets, and decision notes.
- Match saved candidate profiles directly against a structured job payload in Swagger UI.
- List all persisted artifacts via registry endpoints with counts, file listings, and profile status flags.
- Retrieve a summary of all pipeline artifacts in a single registry health call.
- Validate parser and matcher behavior using Pytest unit tests and edge-case scoring tests.
- Validate document-analysis routes with request-level file upload tests using FastAPI TestClient patterns.
- Provide realistic request examples in generated OpenAPI docs through Pydantic schema metadata.

## Processing flow

```text
Candidate document
  -> /documents/analyze-and-save
  -> OCR outputs saved (result.json, text.txt, metadata.json)
  -> /documents/{document_id}/extract-profile
  -> candidate_profile.json saved (with field_confidence)

Raw job description
  -> /jobs/parse
  -> job_profile.json saved (with field_confidence)

Saved candidate profile + saved job profile
  -> /jobs/{job_id}/match/{document_id}
  -> match_result.json saved

Saved candidate profile + structured job payload
  -> /documents/{document_id}/match
  -> direct match response in Swagger/UI

Artifact inspection
  -> /registry/summary         — total counts across all artifact types
  -> /registry/documents       — list all OCR document artifact IDs
  -> /registry/jobs            — list all job profile artifact IDs
  -> /registry/matches         — list all saved match result files
```

## API endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Basic service health check. |
| `/documents/ping` | GET | Verify the documents router is mounted. |
| `/documents/analyze` | POST | Run OCR on an uploaded file and preview extracted text. |
| `/documents/analyze-and-save` | POST | Run OCR on an uploaded file and save OCR outputs. |
| `/documents/{document_id}/extract-profile` | POST | Extract and save a candidate profile from OCR text. |
| `/documents/{document_id}/match` | POST | Match a saved candidate profile to a structured job payload directly in the docs UI. |
| `/jobs/parse` | POST | Parse raw job description text and save a job profile with notes and confidence scores. |
| `/jobs/{job_id}/match/{document_id}` | POST | Match a saved candidate profile to a saved job profile and save the result. |
| `/registry/summary` | GET | Return total counts of all persisted pipeline artifacts. |
| `/registry/documents` | GET | List all saved OCR document artifact IDs and their files. |
| `/registry/documents/{document_id}` | GET | Get artifact file details for a specific document ID. |
| `/registry/jobs` | GET | List all saved job profile artifact IDs and their files. |
| `/registry/jobs/{job_id}` | GET | Get artifact file details for a specific job profile ID. |
| `/registry/matches` | GET | List all saved match result files. |

## Tech stack

| Layer | Tools |
|---|---|
| API backend | FastAPI, Python |
| OCR | Azure Document Intelligence |
| Storage | Azure Blob Storage, local artifact folders |
| Parsing | Python regex and rule-based extraction |
| Confidence scoring | Heuristic field-level confidence (0.0–1.0) on all extracted fields |
| Testing | Pytest, FastAPI TestClient |
| Matching | Deterministic skill-based scoring, evidence snippets, and explainable notes |

## Week 1: Core Pipeline — COMPLETE

Completed deliverables:

Backend services:
- `app/services/candidate_profile_service.py` — OCR to name, email, phone, LinkedIn, GitHub, and skills.
- `app/services/job_profile_service.py` — job text to title, location, years of experience, and required/preferred skills.
- `app/services/matching_service.py` — skills to score, decision, evidence, and notes.

Evaluation framework:
- `scripts/run_evaluation.py` — benchmark runner with 32/32 checks passed.
- `tests/` — unit tests for core parsing and matching services.
- `data/evaluation/` — candidate, job, and match-case fixtures.

Key features delivered:
- Deterministic parsing of identity, contact fields, and skills from OCR text.
- Evidence-aware matching with supporting text snippets.
- Explainable outputs with score, decision, notes, and evidence.
- Production-style evaluation across parsing, matching, and explainability.
- Strong service-level test coverage for core logic.

Portfolio bullets:
- Built a deterministic OCR-to-candidate-job matching pipeline with full benchmark coverage.
- Added evidence tracing and explainable outputs for recruiter auditability.
- Implemented a production-style evaluation framework for parsing, matching, and explainability.

## Week 2: API Integration and Validation — COMPLETE

Week 1 already delivered the full OCR-to-matching pipeline. Week 2 focused on hardening that pipeline at the API layer with cleaner route behavior, realistic interactive testing, better schema examples, stronger job-description parsing, and explicit matcher boundary coverage.

Week 2 improvements:
- Added route-level tests for document analysis, OCR artifact persistence, and profile extraction using FastAPI TestClient upload patterns.
- Standardized the Document Intelligence service boundary around a JSON-safe result payload for persistence and downstream parsing.
- Added a direct structured payload matching path for Swagger testing through `/documents/{document_id}/match`.
- Added realistic request examples to `/jobs/parse` and `/documents/{document_id}/match` using Pydantic schema metadata.
- Improved `job_profile_service.py` with better section-aware parsing, fallback skill extraction, and parser notes for ambiguous job descriptions.
- Added stronger unit tests for structured and unstructured job posts, plus matcher edge cases for strong, moderate, and weak decisions.
- Verified real interactive OCR-to-match smoke tests using a genuine candidate document and a real structured job payload.

## Week 3: Artifact Registry, Confidence Scoring, and Read Path — IN PROGRESS

Week 3 focused on repo hygiene, source-of-truth reset, and two production-depth features that improve observability and output trustworthiness.

Completed milestones:
- Audited and synced repo structure, README, and `.gitignore` to match the actual state of the codebase.
- Untracked all generated runtime data folders from git while preserving evaluation fixtures.
- Added `app/api/routes/registry.py` with 6 endpoints covering artifact listing, detail retrieval, and a summary health call across documents, jobs, and matches.
- Added `field_confidence` scoring to both `candidate_profile_service.py` and `job_profile_service.py` — every extracted field now carries a heuristic confidence float (0.0–1.0) based on extraction method reliability.
- Added `tests/test_registry_route.py` (8 tests) and `tests/test_confidence_scoring.py` (14 tests).
- Full test suite: 34/34 passing across 6 test files.

In progress:
- Saved match retrieval endpoint — `GET /jobs/{job_id}/match/{document_id}` to read a previously saved match from disk without re-running.
- Evaluation harness — `scripts/run_evaluation.py` scored against fixture resumes with expected outputs.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/NANInithin/azure-ocr-job-matcher.git
cd azure-ocr-job-matcher
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file from `.env.example` and set the Azure credentials required by the application.

```env
APP_NAME=Azure Job Application Selector
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=your_endpoint_here
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_key_here
AZURE_DOCUMENT_INTELLIGENCE_MODEL=prebuilt-layout
AZURE_STORAGE_CONNECTION_STRING=your_connection_string_here
AZURE_STORAGE_CONTAINER_RAW=raw-documents
```

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Testing

Run the full test suite with:

```bash
pytest tests -v
```

Current tested areas:
- candidate profile extraction,
- field confidence scoring for candidate profiles,
- field confidence scoring for job profiles,
- job description parsing for structured inputs,
- job description parsing for fallback/unstructured inputs,
- parser notes for ambiguous inputs,
- strong-match behavior,
- weak-match behavior,
- moderate-match boundary behavior,
- matching without preferred skills,
- matching with preferred-only skills,
- document analysis route behavior,
- OCR artifact save flow,
- profile extraction from saved OCR text,
- artifact registry listing (documents, jobs, matches),
- artifact registry 404 handling,
- registry summary counts.

## Evaluation

This project includes an evaluation pack for the OCR-to-profile-to-match pipeline.

### Run the benchmark

```bash
python scripts/run_evaluation.py
```

### Current benchmark results

- Candidate extraction: 12/12 checks passed.
- Job parsing: 10/10 checks passed.
- Matching and explainability: 10/10 checks passed.

### Evaluation scope

Two candidate samples, two job descriptions, and two end-to-end matching cases validate:
- identity field extraction,
- skill extraction from OCR text,
- job parsing,
- matching decisions,
- evidence snippets,
- explanatory notes.

## Example workflow

### 1. Analyze a resume

Use `POST /documents/analyze-and-save` with a candidate PDF or image file.

### 2. Extract a candidate profile

Call `POST /documents/{document_id}/extract-profile` to generate `candidate_profile.json` with field confidence scores.

### 3. Parse a job description

Call `POST /jobs/parse` with raw job text.

Example request:

```json
{
  "job_text": "Computer Vision Engineer\nLocation: France\nWe are looking for a Computer Vision Engineer with 2+ years of experience. Required skills include Python, PyTorch, OpenCV, Docker, and computer vision. Preferred skills include Azure, Kubernetes, CUDA, and TensorFlow."
}
```

### 4. Match candidate to a saved job profile

```text
POST /jobs/{job_id}/match/{document_id}
```

### 5. Match candidate directly to a structured job payload

```text
POST /documents/{document_id}/match
```

Example payload:

```json
{
  "title": "Computer Vision Engineer",
  "company": "Industrial Vision AI",
  "required_skills": ["python", "pytorch", "opencv", "computer vision", "deep learning"],
  "preferred_skills": ["azure", "docker", "kubernetes", "cuda", "tensorflow"],
  "minimum_years_experience": 2,
  "location": "France",
  "remote_ok": true
}
```

### 6. Inspect persisted artifacts

```text
GET /registry/summary
GET /registry/documents
GET /registry/documents/{document_id}
GET /registry/jobs
GET /registry/matches
```

Example summary response:

```json
{
  "total_documents": 10,
  "documents_with_profile": 6,
  "total_jobs": 5,
  "total_matches": 1
}
```

## Resume-ready project bullets

- Built a production-style FastAPI backend for OCR-based job application screening using Azure Document Intelligence and Azure Blob Storage.
- Designed a modular document pipeline for resume ingestion, OCR artifact persistence, candidate profile extraction, job description parsing, and explainable candidate-job matching.
- Implemented deterministic parsing and scoring services that convert unstructured resumes and job descriptions into structured JSON artifacts with per-field confidence scores for reproducible evaluation and debugging.
- Added artifact registry endpoints for real-time inspection of all pipeline outputs — documents processed, profiles extracted, jobs parsed, and matches saved.
- Added unit, route-level, and edge-case tests for parsing, matching, confidence scoring, and OCR-related API flows — 34 tests passing across 6 test files.

## Current limitations

The current extraction logic is intentionally deterministic and lightweight, which makes it easy to debug but less robust than a later section-aware or LLM-assisted parser. The matching logic is still skill-centric and should later be expanded with stronger evidence tracing, experience normalization, education checks, language requirements, and evaluation metrics. Confidence scores are heuristic and not calibrated against ground-truth labels.

## Roadmap

- Add saved match retrieval endpoint to read previously computed results without re-running the pipeline.
- Expand evaluation harness with fixture-based scoring and pass/fail thresholds.
- Add async batch processing for multiple document uploads.
- Expand parsing with section-aware logic and richer evidence spans.
- Add retrieval over OCR outputs for grounded evidence lookup.
- Add background processing and Azure-native deployment.
- Add a recruiter-facing UI after backend stabilization.

## Why this repository is useful

This repository demonstrates practical document intelligence engineering rather than only model experimentation. It emphasizes modular backend design, explainable outputs, field-level confidence scoring, saved artifacts, test coverage, and a realistic OCR-to-decision workflow relevant to AI, ML, CV, and backend-focused roles.
