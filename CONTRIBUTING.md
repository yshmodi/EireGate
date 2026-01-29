# Contributing to EireGate

## Scope
EireGate is a multi-agent system for Irish immigration compliance, job-to-visa gap analysis, and resume tailoring.

## Development setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run API
```bash
cd backend
uvicorn app.main:app --reload
```

## Project conventions
- Agent workflows are **LangGraph state machines** (no linear chains).
- Use **Pydantic models** for all API inputs/outputs.
- Use the **2026 Irish visa thresholds** as source of truth (see README).
- Never commit secrets; use `backend/.env` locally and `backend/.env.example` for templates.

## PR checklist
- Verify API routes under `/api/v1/*`.
- Maintain deterministic visa logic (temperature=0.3 for Gemini).
- Include reasoning in any visa eligibility response.
