from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel
from uuid import uuid4
import PyPDF2
from io import BytesIO

from ...agents.graph import graph

router = APIRouter(prefix="/resume", tags=["resume"])

class ProcessResponse(BaseModel):
    thread_id: str
    parsed_resume: dict | None = None
    tailored_resume: dict | None = None
    match_score: float = 0.0
    visa_advice: str = ""
    salary_gap_analysis: str | None = None
    messages: list[str] = []

@router.post("/process", response_model=ProcessResponse)
async def process_resume(
    file: UploadFile | None = File(None),
    target_role: str = Query(..., description="Target job title, e.g. 'AI Engineer'"),
    target_company: str = Query("", description="Optional: Target company, e.g. 'Stripe Ireland'"),
    proposed_salary: float | None = Query(None, description="Optional proposed annual salary €"),
    thread_id: str = Query(default_factory=lambda: str(uuid4()), description="Session ID (reuse for updates)"),
):
    config = {"configurable": {"thread_id": thread_id}}
    """
    Full pipeline: upload PDF → parse → tailor → match score + visa advice.
    """
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
            "target_role": target_role,
            "target_company": target_company,
            "messages": []
        }
    else:
        current_state = graph.get_state(config)
        if not current_state or "parsed_resume" not in current_state.values:
            raise HTTPException(400, "No active session. Upload PDF first.")

        input_state = {
            "target_role": target_role,
            "target_company": target_company,
            "messages": []
        }

    try:
        result = graph.invoke(input_state, config= config)

        salary_gap = None
        if proposed_salary is not None and result.get("visa_advice"):
            is_recent_grad = "recent" in result["visa_advice"].lower()
            threshold = 36848 if is_recent_grad else 40904
            gap = threshold - proposed_salary
            direction = "below" if gap > 0 else "above"
            salary_gap = (
                f"Proposed €{proposed_salary:,.0f} is €{abs(gap):,.0f} {direction} "
                f"the CSEP threshold (€{threshold:,.0f} {'Graduate Band' if is_recent_grad else 'standard'})."
            )

        return ProcessResponse(
            thread_id=thread_id,
            parsed_resume=result.get("parsed_resume"),
            tailored_resume=result.get("tailored_resume"),
            match_score=result.get("match_score", 0.0),
            visa_advice=result.get("visa_advice", ""),
            salary_gap_analysis=salary_gap,
            messages=[msg.content for msg in result.get("messages", [])]
        )

    except Exception as e:
        raise HTTPException(500, f"Processing failed: {str(e)}")
