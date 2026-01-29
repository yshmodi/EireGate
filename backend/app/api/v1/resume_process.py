from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel

from ...agents.graph import graph
import PyPDF2
from io import BytesIO

router = APIRouter(prefix="/resume", tags=["resume"])

class ProcessResponse(BaseModel):
    parsed_resume: dict
    tailored_resume: dict
    match_score: float
    visa_advice: str
    messages: list[str]

@router.post("/process", response_model=ProcessResponse)
async def process_resume(
    file: UploadFile = File(...),
    target_role: str = Query(..., description="Target job title, e.g. 'AI Engineer'"),
    target_company: str = Query("", description="Optional: Target company, e.g. 'Stripe Ireland'"),
):
    """
    Full pipeline: upload PDF → parse → tailor → match score + visa advice.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    try:
        contents = await file.read()
        pdf_file = BytesIO(contents)
        reader = PyPDF2.PdfReader(pdf_file)
        raw_text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            raw_text += page_text + "\n\n"

        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="No readable text extracted from PDF")

        # Invoke the LangGraph state machine
        result = graph.invoke({
            "raw_text": raw_text,
            "target_role": target_role,
            "target_company": target_company,
            "messages": []
        })

        return ProcessResponse(
            parsed_resume=result.get("parsed_resume", {}),
            tailored_resume=result.get("tailored_resume", {}),
            match_score=result.get("match_score", 0.0),
            visa_advice=result.get("visa_advice", "No visa advice generated."),
            messages=[msg.content for msg in result.get("messages", [])]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
