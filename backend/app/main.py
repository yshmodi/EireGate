from fastapi import FastAPI, Query

from app.api.v1.resume import router as resume_router
from app.api.v1.resume_tailor import router as tailor_router
from app.api.v1.resume_process import router as process_router
from app.api.v1.jobs import router as jobs_router
from app.core.llm_router import get_llm_status, test_provider, test_all_providers
from app.api.v1.auth import router as auth_router

app = FastAPI(title="EireGate API", version="0.1.0")

app.include_router(resume_router, prefix="/api/v1")
app.include_router(tailor_router, prefix="/api/v1")
app.include_router(process_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/health/llm")
def llm_health_check() -> dict:
    """Get status of all LLM providers."""
    return get_llm_status()


@app.get("/health/llm/test")
def test_all_llm_providers() -> dict:
    """
    Test ALL LLM providers with a simple prompt.
    Returns success/failure and response time for each.
    ⚠️ This will make one API call to each provider!
    """
    return test_all_providers()


@app.get("/health/llm/test/{provider_name}")
def test_single_llm_provider(provider_name: str) -> dict:
    """
    Test a specific LLM provider.

    Valid providers: Gemini, OpenRouter, Mistral, HuggingFace
    """
    return test_provider(provider_name)
