# EireGate

EireGate is a production-grade multi-agent system that helps non-EEA graduates in Ireland navigate 2026 immigration rules, run **job-to-visa gap analysis**, and tailor resumes for Irish employers.

## Why EireGate
- **Visa compliance**: Uses the 2026 Irish employment permit thresholds as source of truth.
- **Job-to-visa alignment**: Evaluates salary and role fit (CSEP/GEP) with clear reasoning.
- **Resume optimization**: Parses and structures resumes for Irish market requirements.

## Core Stack
- **Agents**: LangGraph (state machine workflows)
- **Backend**: FastAPI + Pydantic
- **LLM**: Google Gemini via `langchain_google_genai`
- **Resume parsing**: PyPDF2

## 2026 Irish Visa Thresholds (Source of Truth)
| Permit Type | General Salary Threshold | Recent Grad Threshold | Notes |
|---|---|---|---|
| **CSEP** (Critical Skills) | €40,904 | €36,848 | Effective March 1, 2026 |
| **GEP** (General) | €36,605 | €34,009 | For all occupations |
| **Stamp 1G** | — | 24 months | Master's degree holders only |

Critical skills focus: **AI Engineer**, **Data Scientist**, **Software Engineer**.

## Project Structure
```
backend/
  app/
    api/v1/          # FastAPI route handlers
    models/          # Pydantic models
    services/        # LLM + parsing services
  .env.example       # Environment template
requirements.txt
```

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run the API
```bash
cd backend
uvicorn app.main:app --reload
```

### Health Check
```
GET /health
```

### Resume Upload
```
POST /api/v1/resume/upload
```

## Environment
Create a `.env` in `backend/` with:
```
GOOGLE_API_KEY=your_google_api_key_here
```

## Notes
- Do **not** commit `.env` (it is ignored by default).
- Agent logic should be modeled as **state graphs** (LangGraph), not linear pipelines.

## License
TBD
