# AI-Powered Resume Generation Backend

A production-grade, highly scalable backend for generating AI-optimized, role-specific LaTeX resumes dynamically.

## 🚀 Overview

This backend system acts as the engine for a dynamic AI resume platform. It uses a structured JSON profile as the single source of truth and can generate tailored, ATS-optimized PDF resumes for various roles (e.g., AI Engineer, Backend Engineer, Startup, Executive) dynamically.

## 🏗️ Architecture

The project is built using modern Domain-Driven Design (DDD) principles:

- **Framework:** FastAPI (Async-first, high concurrency)
- **Database:** MongoDB (via Motor async driver)
- **Data Validation:** Pydantic v2
- **Templating:** Jinja2 + LaTeX (`pdflatex`)
- **AI Integration:** NVIDIA API (Qwen model) for JD parsing and bullet rewriting
- **JD Scoring:** Keyword-based profile matching against extracted JD keywords

### Project Structure
```text
app/
├── api/             # FastAPI routers (Profiles, Resumes, JD)
├── core/            # Config, MongoDB connections
├── schemas/         # Pydantic validation schemas
├── services/        # Business logic layer
├── repositories/    # MongoDB data access layer
├── templates/       # ATS + visual Jinja2 LaTeX templates
├── generators/      # Subprocess PDF compiler
└── ai/              # NVIDIA API wrapper and Prompts
```

## 🛠️ Features

1. **Profile Engine:** Validates massive structured JSON profiles.
2. **Template Engine:** Injects JSON data into 7 bespoke `.tex.j2` templates, including a default single-column ATS-optimized template, using custom `\BLOCK{}` and `\VAR{}` delimiters to prevent LaTeX syntax collisions.
3. **JD Optimization Engine:** Extracts `skills`, `keywords`, and `role requirements` from raw job descriptions using an LLM.
4. **JD Scoring:** Scores resume profiles against extracted JD keywords.
5. **ATS Readiness Check:** Scores generated templates against ATS-safe formatting and content rules with a target range of `80-95`.
6. **PDF Metadata:** Injects author, title, subject, creator, and keyword metadata into generated PDFs.
7. **AI Rewriter:** Dynamically rewrites resume bullet points using the NVIDIA API to increase ATS density and match job expectations.

## 💻 Running Locally

### Prerequisites
You need Python 3.11+ and LaTeX installed on your system.

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install -y texlive-latex-base texlive-fonts-recommended texlive-fonts-extra texlive-latex-extra
```
*(Note: `texlive-fonts-extra` is critical for the `fontawesome5` package used in the templates).*

### Using the Helper Script
The easiest way to run the backend is using the included script.
Ensure you set your NVIDIA API key in the terminal first:

```bash
export NVIDIA_API_KEY="nvapi-YOUR-API-KEY"
./run_local.sh
```

### Using Docker
```bash
export NVIDIA_API_KEY="nvapi-YOUR-API-KEY"
docker compose up --build
```

## 🔁 Workflow

The backend is built around one structured profile JSON document. That profile becomes the source of truth for every generated resume.

1. **Create or update a profile**
   Send the master resume JSON to `POST /api/v1/profiles/`. The API validates it with Pydantic and stores it in MongoDB.

2. **Choose a template**
   Use the default `00_ats_optimized.tex.j2` for job applications and ATS uploads. Use the visual templates only when a human-designed PDF is more important than parser score.

3. **Check ATS readiness**
   Call `GET /api/v1/resume/ats-score/{profile_id}` before generating the final PDF. The target score range is `80-95`; the default ATS template is designed to stay in that band.

4. **Generate the PDF**
   Call `POST /api/v1/resume/generate/{profile_id}`. The service renders LaTeX through Jinja2, injects PDF metadata, compiles with `pdflatex`, and returns the PDF bytes.

5. **Optimize for a job description**
   Use `POST /api/v1/jd/analyze` to extract JD keywords and `POST /api/v1/jd/score/{profile_id}` to compare the profile against that JD. The AI helper can also rewrite bullets using the NVIDIA API when `NVIDIA_API_KEY` is configured.

6. **Generate a JD-tailored resume**
   Call `POST /api/v1/resume/generate-from-jd/{profile_id}` with `{"text": "job description..."}`. The service analyzes the JD, prioritizes matching skills/projects/experience already present in the profile, then returns a tailored PDF. If the NVIDIA API key is unavailable, it falls back to local keyword extraction.

### ATS Notes

- Prefer the default ATS template for submissions.
- Keep links visible as full URLs so parsers can read them.
- Keep sections standard: `Professional Summary`, `Skills`, `Work Experience`, `Projects`, and `Education`.
- Avoid relying on visual-only templates for ATS scoring; sidebars, tables, boxes, and multi-column layouts can lower parser confidence.
- PDF metadata is injected automatically from the profile: author, title, subject, keywords, and creator.

## 🧪 API Endpoints

Once the server is running, visit `http://localhost:8000/docs` to see the Swagger UI.

- `POST /api/v1/profiles/` - Create a master profile.
- `GET /api/v1/profiles/{id}` - Retrieve a profile.
- `POST /api/v1/resume/generate/{id}?template=...` - Generate a PDF resume (default: `00_ats_optimized.tex.j2`).
- `POST /api/v1/resume/generate-from-jd/{id}?template=...` - Generate a JD-tailored PDF resume.
- `GET /api/v1/resume/ats-score/{id}?template=...` - Estimate ATS readiness before submitting.
- `POST /api/v1/jd/analyze` - Extract details from raw JD text.
- `POST /api/v1/jd/score/{id}` - Score a profile against a JD.
