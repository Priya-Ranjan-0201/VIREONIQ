from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import Dict, Any
import pypdf
import io
import magic

from db.models import User
from api import deps
from services import syllabus_service

router = APIRouter()

MAX_SYLLABUS_BYTES = 10 * 1024 * 1024


@router.post("/optimize", response_model=Dict[str, Any])
async def optimize_syllabus_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """
    Upload a PDF syllabus, extract text, validate MIME type with python-magic,
    and generate an industry gap alignment report.
    """
    # 1. Extract and validate bytes
    contents = await file.read()
    if len(contents) > MAX_SYLLABUS_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Syllabus PDF exceeds maximum size limit (10MB)."
        )

    detected_mime = magic.from_buffer(contents, mime=True)
    if detected_mime != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF syllabus files are allowed."
        )

    try:
        pdf_reader = pypdf.PdfReader(io.BytesIO(contents))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to parse PDF document."
        )
    
    # 2. Optimize syllabus content
    return await syllabus_service.optimize_syllabus(text)

