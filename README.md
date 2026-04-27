# Azure Job Application Selector







A production-style OCR and document intelligence backend that analyzes candidate application documents, extracts structured profiles, parses job descriptions, and computes explainable candidate-job match results using Azure services and FastAPI.

## Why this project

This project is being built as an 8-week portfolio system focused on recruiter-visible engineering depth in OCR, backend orchestration, structured extraction, reproducible artifacts, and explainable matching workflows.
The backend follows a modular FastAPI structure with routers, schemas, and service layers, which aligns with common FastAPI organization patterns for larger applications.

## Current status

The current implementation supports candidate OCR processing, candidate profile extraction, job description parsing, saved-profile matching, and service-layer unit tests for key parsing and matching logic.
The project now includes reproducible saved artifacts for OCR outputs, job profiles, and match results, which makes debugging and evaluation easier in document intelligence systems.

## Architecture

```mermaid
flowchart TD
    A[Candidate Resume PDF/Image] --> B[/documents/analyze-and-save/]
    B --> C[Azure Document Intelligence OCR]
    C --> D[OCR JSON + text + metadata]

    D --> E[/documents/{document_id}/extract-profile/]
    E --> F[Candidate Profile JSON]

    G[Raw Job Description Text] --> H[/jobs/parse/]
    H --> I[Job Profile JSON]

    F --> J[/jobs/{job_id}/match/{document_id}/]
    I --> J
    J --> K[Match Result JSON]
```

The backend is organized so document ingestion, parsing, and matching logic remain separated instead of being coupled inside one script, which makes later extension into evaluation, async processing, and retrieval easier.

## Project structure

```text
.
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── health.py
│   │       ├── documents.py
│   │       └── jobs.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
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
│   ├── job_profiles/
│   ├── match_results/
│   ├── ocr_outputs/
│   └── uploads/
├── tests/
│   ├── conftest.py
│   ├── test_candidate_profile_service.py
│   ├── test_job_profile_service.py
│   └── test_matching_service.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Features

- Upload candidate documents and process them with Azure Document Intelligence OCR.
- Save OCR artifacts as raw JSON, plain text, and metadata for each document.
- Extract structured candidate profile fields from OCR output using deterministic parsing rules.
- Parse raw job descriptions into title, location, skills, and years of experience.
- Match saved candidate profiles against saved job profiles with transparent scoring and decision logic.
- Validate parser and matcher behavior using Pytest unit tests.

## Processing flow

```text
Candidate document
  -> /documents/analyze-and-save
  -> OCR outputs saved
  -> /documents/{document_id}/extract-profile
  -> candidate_profile.json saved

Raw job description
  -> /jobs/parse
  -> job_profile.json saved

Saved candidate profile + saved job profile
  -> /jobs/{job_id}/match/{document_id}
  -> match_result.json saved
```

## API endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Basic service health check. |
| `/documents/analyze-and-save` | POST | Run OCR on an uploaded file and save OCR outputs. |
| `/documents/{document_id}/extract-profile` | POST | Extract and save a candidate profile from OCR text. |
| `/jobs/parse` | POST | Parse raw job description text and save a job profile. |
| `/jobs/{job_id}/match/{document_id}` | POST | Match a saved candidate profile to a saved job profile and save the result. |

## Tech stack

| Layer | Tools |
|---|---|
| API backend | FastAPI, Python |
| OCR | Azure Document Intelligence |
| Storage | Azure Blob Storage, local artifact folders |
| Parsing | Python regex and rule-based extraction. |
| Testing | Pytest |
| Matching | Deterministic skill-based scoring and explainable notes. |

## Week 1: Core Pipeline - COMPLETE

Completed deliverables:

Backend Services:
- app/services/candidate_profile_service.py  (OCR -> name/email/phone/linkedin/github/skills)
- app/services/job_profile_service.py        (OCR -> title/location/YOE/required+preferred skills)  
- app/services/matching_service.py           (Skills -> score + decision + evidence + notes)

Evaluation Framework:
- scripts/run_evaluation.py                  (32/32 checks passed)
- tests/                                    (4 unit tests passed)
- data/evaluation/                          (2 candidates + 2 jobs + 2 match cases)

Key Features Delivered:
- Deterministic parsing of identity/contact/skills from OCR text
- Evidence-aware matching with supporting text snippets  
- Explainable outputs (score/decision/notes/evidence)
- Production-style evaluation (32 checks: parsing/matching/explainability)
- 100% test coverage on core logic

Technical depth demonstrated:
- Rule-based OCR post-processing
- Backend service architecture
- Explainability & auditability
- Integration testing patterns

Portfolio bullets:
- Built deterministic OCR->candidate-job matching pipeline (100% eval pass rate)
- Added evidence tracing + explainable outputs for recruiter auditability  
- Production evaluation framework (32 checks: parsing/matching/explainability)


## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo-folder>
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
AZURE_STORAGE_CONNECTION_STRING=your_connection_string_here
AZURE_STORAGE_CONTAINER_NAME=job-applications
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

Run the service-layer tests with:

```bash
pytest tests -v
```

Current tested areas:
- candidate profile extraction,
- job description parsing,
- strong-match behavior,
- weak-match behavior. 

## Evaluation

This project includes a comprehensive evaluation pack for the full pipeline: OCR parsing -> skill extraction -> matching -> explainability.

### Run the benchmark

```bash
python scripts/run_evaluation.py
```

### Current benchmark results - 100% PASS ✅

- Candidate extraction: 12/12 checks passed
- Job parsing: 10/10 checks passed  
- Matching + Explainability: 10/10 checks passed

### Evaluation scope

2 candidate samples, 2 job descriptions, 2 end-to-end matching cases with:
- Identity field extraction (name/email/phone/LinkedIn/GitHub)
- Skill extraction from OCR text
- Job parsing (title/location/YOE/required+preferred skills)
- Matching decisions with evidence tracing
- Explainability validation (evidence dict + notes present)

### What the benchmark validates

- Candidate identity fields extracted correctly
- Skills extracted from OCR text  
- Job requirements parsed accurately
- Matching decisions (strong/weak) correct
- Evidence snippets present for matched skills
- Explanatory notes generated for every case

### Week 1 Status

Complete - 100% benchmark pass rate across parsing + matching + explainability.

Ready for Week 2: API integration + end-to-end OCR->match flow.

## Example workflow

### 1. Analyze a resume

Use `POST /documents/analyze-and-save` with a candidate PDF or image file.

### 2. Extract a candidate profile

Call `POST /documents/{document_id}/extract-profile` to generate `candidate_profile.json`.

### 3. Parse a job description

Call `POST /jobs/parse` with raw job text.

Example request:

```json
{
  "job_text": "Computer Vision Engineer\nLocation: France\nWe are looking for a Computer Vision Engineer with 2+ years of experience. Required skills include Python, PyTorch, OpenCV, Docker, and computer vision. Preferred skills include Azure, Kubernetes, CUDA, and TensorFlow."
}
```

### 4. Match candidate to job

Call:

```text
POST /jobs/{job_id}/match/{document_id}
```

Example match output:

```json
{
  "job_title": "Computer Vision Engineer",
  "candidate_name": "Nithin Sai Kumar Kopparapu",
  "matched_required_skills": ["computer vision", "docker", "opencv", "python", "pytorch"],
  "missing_required_skills": [],
  "matched_preferred_skills": ["cuda", "kubernetes", "tensorflow"],
  "score": 95,
  "decision": "strong_match"
}
```

## Resume-ready project bullets

- Built a production-style FastAPI backend for OCR-based job application screening using Azure Document Intelligence and Azure Blob Storage.
- Designed a modular document pipeline for resume ingestion, OCR artifact persistence, candidate profile extraction, job description parsing, and explainable candidate-job matching.
- Implemented deterministic parsing and scoring services that convert unstructured resumes and job descriptions into structured JSON artifacts for reproducible evaluation and debugging.
- Added unit tests for parsing and matching services to improve reliability and refactoring safety.

## Current limitations

The current extraction logic is intentionally deterministic and lightweight, which makes it easy to debug but less robust than a later section-aware or LLM-assisted parser.
The matching logic is still skill-centric and should later be expanded with stronger evidence tracing, experience normalization, education checks, language requirements, and evaluation metrics.

## Roadmap

- Add evaluation datasets and extraction quality metrics.
- Expand parsing with section-aware logic and evidence spans.
- Add retrieval over OCR outputs for grounded evidence lookup.
- Add background processing and Azure-native deployment.
- Add a recruiter-facing UI after backend stabilization.

## Why this repository is useful

This repository demonstrates practical document intelligence engineering rather than only model experimentation.
It emphasizes modular backend design, explainable outputs, saved artifacts, test coverage, and a realistic OCR-to-decision workflow relevant to AI, ML, CV, and backend-focused roles.