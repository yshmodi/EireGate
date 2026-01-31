# Contributing to EireGate

## Scope
EireGate is an AI-powered job matching platform that analyzes resumes and finds best-fit jobs globally with smart match scores.

## Development Setup
```bash
conda activate eiregate
pip install -r requirements.txt
```

## Run API
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

## Project Conventions
- Agent workflows use **LangGraph state machines** (not linear chains)
- Use **Pydantic models** for all API inputs/outputs
- Use the **Multi-LLM Router** (`core/llm_router.py`) for all LLM calls
- Never commit secrets; use `.env` locally and `.env.example` for templates
- Log with `loguru`, not `print()`

## PR Checklist
- [ ] API routes under `/api/v1/*`
- [ ] LLM calls use `invoke_with_fallback()` from llm_router
- [ ] New endpoints have Pydantic request/response models
- [ ] No hardcoded API keys
