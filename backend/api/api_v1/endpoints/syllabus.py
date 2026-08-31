from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import PyPDF2
import io
import magic

from db.session import get_db
from db.models import User
from api import deps
from services import syllabus_service

router = APIRouter()


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
    
    detected_mime = magic.from_buffer(contents, mime=True)
    if detected_mime != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF syllabus files are allowed."
        )
        
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse PDF document: {str(e)}"
        )
    
    # 2. Optimize syllabus content
    return await syllabus_service.optimize_syllabus(text)

