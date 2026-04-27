# Azure Job Application Selector

A production-style OCR and document intelligence backend that analyzes candidate application documents, extracts structured profiles, parses job descriptions, and computes explainable candidate-job match results using Azure services and FastAPI.[1][2]

## Overview

This project is being built as an 8-week portfolio system focused on recruiter-visible engineering depth in OCR, backend orchestration, structured extraction, and grounded matching workflows.[3][2]
The current backend uses a modular FastAPI application structure with separate routers and services, which aligns with common FastAPI project organization practices for larger applications.[1][4][5]

## Current capabilities

- Upload candidate documents through FastAPI and process them with Azure Document Intelligence for OCR and text extraction.[2]
- Save OCR artifacts for each document, including raw JSON, plain text, and metadata, to support debugging and later evaluation.[6][2]
- Extract candidate profile fields such as name, email, phone, links, and skills from OCR text using deterministic parsing rules.[6]
- Parse raw job descriptions into structured job profiles containing title, location, required skills, preferred skills, and years of experience.[7]
- Match saved candidate profiles to saved job profiles with transparent scoring, matched skills, missing skills, and a final decision label.[7]

## Architecture

The backend is organized into routers, schemas, core configuration, and service modules so that document ingestion, parsing, and matching logic stay separated instead of being merged into one script.[1][5]
This structure makes it easier to extend the system later with background jobs, databases, evaluation pipelines, and retrieval or grounded Q&A components.[4][2]

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
├── .env.example
├── requirements.txt
└── README.md
```

## Processing flow

The current end-to-end pipeline is candidate document upload -> OCR extraction -> OCR artifact storage -> candidate profile extraction -> job description parsing -> saved-profile matching.[6][2]
Each stage writes intermediate files so the pipeline is reproducible and easy to inspect during development, which is especially useful for OCR-heavy systems where extraction quality must be verified step by step.[6]

```text
Candidate PDF/Image
        |
        v
/documents/analyze-and-save
        |
        v
OCR JSON + text + metadata saved
        |
        v
/documents/{document_id}/extract-profile
        |
        v
candidate_profile.json saved

Raw job description text
        |
        v
/jobs/parse
        |
        v
job_profile.json saved
        |
        v
/jobs/{job_id}/match/{document_id}
        |
        v
match_result.json saved
```

## API endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Basic service health check. |
| `/documents/analyze-and-save` | POST | Run OCR on an uploaded file and save raw OCR outputs. |
| `/documents/{document_id}/extract-profile` | POST | Extract and save a structured candidate profile from saved OCR text. |
| `/jobs/parse` | POST | Parse raw job description text and save a structured job profile. |
| `/jobs/{job_id}/match/{document_id}` | POST | Match a saved candidate profile against a saved job profile and save the result. |

## Tech stack

| Layer | Tools |
|---|---|
| API backend | FastAPI, Python[8] |
| OCR | Azure Document Intelligence[2] |
| Storage | Azure Blob Storage, local artifact folders[2] |
| Parsing | Regex and rule-based extraction with Python `re`.[7][9] |
| Matching | Deterministic skill-based scoring and explainable notes. |

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

Create a `.env` file from `.env.example` and set the Azure credentials needed by the application.

Example variables:

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

After startup, open:

```text
http://127.0.0.1:8000/docs
```

## Example workflow

### 1. Analyze a resume

Use `POST /documents/analyze-and-save` with a PDF or image resume to create saved OCR outputs under `data/ocr_outputs/<document_id>/`.

### 2. Extract a candidate profile

Call `POST /documents/{document_id}/extract-profile` to create `candidate_profile.json` from the saved OCR text.

### 3. Parse a job description

Send raw job text to `POST /jobs/parse` to generate a saved job profile under `data/job_profiles/<job_id>/`.

Example request body:

```json
{
  "job_text": "Computer Vision Engineer\nLocation: France\nWe are looking for a Computer Vision Engineer with 2+ years of experience. Required skills include Python, PyTorch, OpenCV, Docker, and computer vision. Preferred skills include Azure, Kubernetes, CUDA, and TensorFlow."
}
```

### 4. Match candidate to job

Call `POST /jobs/{job_id}/match/{document_id}` to generate a saved match artifact under `data/match_results/`.

## Current limitations

The current extraction logic is intentionally deterministic and lightweight, which makes it easy to debug but less robust than a later LLM-assisted or section-aware parser.[7][2]
The matching logic is currently skill-focused and should later be expanded with stronger evidence tracing, experience normalization, education checks, language requirements, and evaluation metrics.[2]

## Roadmap

- Add unit tests for parsing and matching logic.
- Add evaluation datasets and extraction accuracy metrics.
- Improve section-aware parsing for resumes and job descriptions.
- Add retrieval over OCR outputs for grounded evidence lookup.
- Add Azure-native async processing and deployment paths.
- Add a recruiter-facing UI or demo dashboard after backend stabilization.

## Why this project matters

This project is designed to demonstrate practical document intelligence engineering rather than only model experimentation.[2]
It emphasizes reproducible artifacts, explainable matching, modular backend design, and a realistic OCR-to-decision workflow that is relevant for AI, ML, CV, and backend-oriented roles.[1][5][3]