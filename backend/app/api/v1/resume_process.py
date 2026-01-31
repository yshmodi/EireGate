from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel
from uuid import uuid4
import PyPDF2
import json
from io import BytesIO

from ...agents.graph import graph
from ...core.cache import redis

router = APIRouter(prefix="/resume", tags=["resume"])


class ProcessResponse(BaseModel):
    thread_id: str
    parsed_resume: dict | None = None
    tailored_resume: dict | None = None
    match_score: float = 0.0
    job_used: dict | None = None
    messages: list[str] = []


@router.post("/process", response_model=ProcessResponse)
async def process_resume(
    file: UploadFile | None = File(None),
    job_id: str | None = Query(None, description="Job ID from /jobs/search — auto-fills role, company"),
    target_role: str | None = Query(None, description="Target job title (auto-filled if job_id provided)"),
    target_company: str | None = Query(None, description="Target company (auto-filled if job_id provided)"),
    thread_id: str = Query(default_factory=lambda: str(uuid4()), description="Session ID (reuse for updates)"),
):
    """
    Resume tailoring pipeline.

    1. Upload PDF → Parse resume
    2. Tailor for specific JD if job_id provided
    3. Returns tailored summary, achievement bullets, and skills
    """
    config = {"configurable": {"thread_id": thread_id}}

    jd_text = ""
    job_used = None

    # Fetch job details from cache if job_id provided
    if job_id:
        if not redis:
            raise HTTPException(503, "Cache unavailable. Provide target_role manually.")

        found = False
        for key in redis.scan_iter("jobs:*"):
            cached = redis.get(key)
            if cached:
                jobs = json.loads(cached)
                for job in jobs:
                    if job.get("id") == job_id:
                        jd_text = job.get("description", "")
                        target_role = target_role or job.get("title", "Software Engineer")
                        target_company = target_company or job.get("company", "")

                        job_used = {
                            "id": job_id,
                            "title": job.get("title"),
                            "company": job.get("company"),
                            "location": job.get("location", ""),
                            "url": job.get("url")
                        }
                        found = True
                        break
                if found:
                    break

        if not found:
            raise HTTPException(404, f"Job '{job_id}' not found in cache. Run /jobs/search first.")

    # Require target_role if no job_id
    if not target_role:
        raise HTTPException(400, "target_role is required when job_id is not provided")

    if file:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files allowed")

        contents = await file.read()
        pdf_file = BytesIO(contents)
        reader = PyPDF2.PdfReader(pdf_file)
        raw_text = "".join(page.extract_text() or "" for page in reader.pages).strip()

        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="No readable text extracted from PDF")

        input_state = {
            "raw_text": raw_text,
            "jd_text": jd_text,
            "target_role": target_role,
            "target_company": target_company or "",
            "messages": []
        }
    else:
        current_state = graph.get_state(config)
        if not current_state or "parsed_resume" not in current_state.values:
            raise HTTPException(400, "No active session. Upload PDF first.")

        input_state = {
            "jd_text": jd_text,
            "target_role": target_role,
            "target_company": target_company or "",
            "messages": []
        }

    try:
        result = graph.invoke(input_state, config=config)

        return ProcessResponse(
            thread_id=thread_id,
            parsed_resume=result.get("parsed_resume"),
            tailored_resume=result.get("tailored_resume"),
            match_score=result.get("match_score", 0.0),
            job_used=job_used,
            messages=[msg.content for msg in result.get("messages", [])]
        )

    except Exception as e:
        raise HTTPException(500, f"Processing failed: {str(e)}")
