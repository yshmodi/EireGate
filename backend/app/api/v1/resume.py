from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
import PyPDF2
from io import BytesIO
import logging

from ...services.resume_parser import parse_resume
from ...models.resume import Resume

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/upload", response_model=Resume)
async def upload_and_parse_resume(file: UploadFile = File(...)):
    """Uploads PDF resume -> extract text -> parse into structtured Resume model using Gemini.
    Returns structured data + visa notes.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are supported.")
    if file.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 5MB)")
    try:
        contents = await file.read()
        pdf_file = BytesIO(contents)
        reader = PyPDF2.PdfReader(pdf_file)

        raw_text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            raw_text += page_text + "\n\n"

        if not raw_text.strip():
            raise ValueError("No readable text extracted from PDF.")

        parsed_resume: Resume = parse_resume(raw_text)

        return JSONResponse(
            content={
                "status": "success",
                "parsed_resume": parsed_resume.model_dump(),
                "visa_summary": f"Eligible for up to {parsed_resume.visa_notes.get('stamp_1g_months', 'unknown')} months Stamp 1G"
            },
            status_code=200
        )
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")
