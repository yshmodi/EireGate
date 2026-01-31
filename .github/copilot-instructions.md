# EireGate: Copilot Instructions for AI Coding Agents

## Project Overview
EireGate is an **AI-powered job matching platform** that analyzes resumes and finds the best-fit jobs globally. It uses **LangGraph** (state machine agents), **FastAPI** (backend), and **Next.js** (frontend).

**Core Domain**: Resume parsing, job matching, skill alignment scoring, and job search aggregation.

---

## Architecture Decisions

### Backend: LangGraph Agents (State Machine Mindset)
- **Never** model agents as pipelines; use **checkpoints & persistence**
- Each agent is a state graph: `state = {"context": {...}, "messages": [], "decisions": {}}`
- Example agents: `ResumeParserAgent`, `JobMatcherAgent`, `ResumeTailorAgent`
- Use `langgraph.graph.StateGraph` for composing multi-step workflows

### API Layer: FastAPI
- All endpoints return **structured Pydantic responses**
- Endpoints follow: `/api/v1/{resource}/{action}` (e.g., `/api/v1/resume/upload`)
- Include request validation with `pydantic_settings` for secrets (.env integration)

### Multi-LLM Router
- Primary: Google Gemini (`gemini-2.0-flash`)
- Fallbacks: OpenRouter, Mistral, HuggingFace
- All providers are free-tier compatible
- Use `invoke_with_fallback()` from `core/llm_router.py` for automatic failover

---

## Code Patterns

### Pydantic Models (Production Standard)
```python
from pydantic import BaseModel, Field

class JobPosting(BaseModel):
    title: str = Field(..., description="Job title")
    company: str
    location: str
    skills: list[str]
    url: str

class MatchScore(BaseModel):
    score: float = Field(..., ge=0, le=100)
    matched_skills: list[str]
    missing_skills: list[str]
```

### LangGraph Agent Pattern
```python
from langgraph.graph import StateGraph
from typing import TypedDict

class AgentState(TypedDict):
    raw_text: str
    parsed_resume: dict
    target_role: str
    messages: list[dict]

def extract_node(state: AgentState) -> AgentState:
    # Parse resume logic here
    return state

graph = StateGraph(AgentState)
graph.add_node("extract", extract_node)
# ... add more nodes and edges
```

### Error Handling
- Use `HTTPException` with 400/422 for validation errors
- Use custom domain exceptions: `ResumeParseError`, `JobNotFoundError`
- Always log with `loguru` (not print)

---

## Developer Workflows

### Setup
```bash
conda activate eiregate
cd backend
pip install -r requirements.txt
```

### Running Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Testing LLM Providers
```bash
curl http://localhost:8000/health/llm/test
```

---

## Key Files

| File | Purpose |
|------|---------|
| `core/llm_router.py` | Multi-LLM router with automatic fallback |
| `agents/graph.py` | LangGraph workflow definition |
| `agents/nodes.py` | Agent node functions (extract, tailor) |
| `services/resume_parser.py` | LLM-powered resume parsing |
| `services/resume_tailor.py` | Resume tailoring + match scoring |
| `services/job_service.py` | JobSpy wrapper for job search |

---

## Avoid These Patterns

- ❌ Building agents without state graphs (use LangGraph, not chains)
- ❌ Hardcoding API keys (use .env)
- ❌ Async/await without proper error boundaries
- ❌ Unvalidated user input to LLM (always sanitize + validate first)
- ❌ Using print() instead of loguru logger

---

## References

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [JobSpy Documentation](https://github.com/Bunsly/JobSpy)
