# EireGate: Copilot Instructions for AI Coding Agents

## Project Overview
EireGate is a **multi-agent agentic system** helping non-EEA graduates navigate 2026 Irish immigration and secure employment. It uses **LangGraph** (state machine agents), **FastAPI** (backend), and **Next.js** (frontend).

**Core Domain**: Irish employment permits, visa thresholds, job-to-resume alignment, and critical skills matching.

---

## 2026 Irish Immigration Thresholds (Source of Truth)

Use these exact figures in all agent responses and code logic:

| Permit Type | General Salary Threshold | Recent Grad Threshold | Notes |
|---|---|---|---|
| **CSEP** (Critical Skills) | €40,904 | €36,848 | Effective March 1, 2026 |
| **GEP** (General) | €36,605 | €34,009 | For all occupations |
| **Stamp 1G** | — | 24 months | Master's degree holders only |

**Critical Skills List** (prioritize): AI Engineer, Data Scientist, Software Engineer

---

## Architecture Decisions

### Backend: LangGraph Agents (State Machine Mindset)
- **Never** model agents as pipelines; use **checkpoints & persistence**
- Each agent is a state graph: `state = {"context": {...}, "messages": [], "decisions": {}}`
- Example agents: `JobAnalyzerAgent`, `VisaEligibilityAgent`, `ResumeOptimizerAgent`
- Use `langgraph.graph.StateGraph` for composing multi-step workflows

### API Layer: FastAPI
- All endpoints return **structured Pydantic responses**
- Use `fastapi.background_tasks` for long-running agent workflows
- Endpoints follow: `/api/{agent}/{action}` (e.g., `/api/visa/check-eligibility`)
- Include request validation with `pydantic_settings` for secrets (.env integration)

### Integration with Google Gemini
- Use `langchain_google_genai` (v4.2.0+) for LLM calls
- Set `temperature=0.3` for deterministic visa/compliance decisions
- Implement retry logic with `tenacity` (9.0.0+) for API resilience

---

## Code Patterns

### Pydantic Models (Production Standard)
```python
from pydantic import BaseModel, Field

class JobPosting(BaseModel):
    title: str = Field(..., description="Job title")
    salary_eur: float = Field(..., ge=0)
    years_required: int
    skills: list[str]

class VisaCheckResult(BaseModel):
    permit_type: str  # "CSEP" | "GEP"
    eligible: bool
    gap_eur: float  # Salary shortfall from threshold
    reasoning: str
```

### LangGraph Agent Pattern
```python
from langgraph.graph import StateGraph
from typing import TypedDict

class AgentState(TypedDict):
    job_posting: JobPosting
    candidate_salary: float
    messages: list[dict]

def visa_check_node(state: AgentState) -> AgentState:
    # Agent logic here
    return state

graph = StateGraph(AgentState)
graph.add_node("visa_check", visa_check_node)
# ... add more nodes and edges
```

### Error Handling
- Use `HTTPException` with 400/422 for validation errors
- Use custom domain exceptions: `IneligibleForVisaError`, `ResumeParseError`
- Always log with `loguru` (not print)

---

## Developer Workflows

### Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running Backend
```bash
cd backend
uvicorn main:app --reload
```

### Testing Agents Locally
- Mock Google Gemini with `langchain.llm_cache` or fixture
- Use `langgraph` built-in visualization: `graph.get_graph().draw_ascii()`

---

## Key Integration Points

1. **Resume → Job Matching**: Parse PDF (PyPDF2) → extract skills → match against job posting
2. **Salary Validation**: Compare offered salary against permit thresholds + cost-of-living adjustments
3. **Visa Eligibility**: Route through CSEP → GEP based on skill criticality and salary
4. **Compliance Logging**: All visa decisions must include reasoning + timestamp

---

## Avoid These Patterns

- ❌ Building agents without state graphs (use LangGraph, not chains)
- ❌ Hardcoding salary thresholds in prompts (centralize in config)
- ❌ Async/await without proper error boundaries
- ❌ Unvalidated user input to LLM (always sanitize + validate first)

---

## References

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- Irish Immigration Bureau 2026 Salary Thresholds (March 1 effective date)
