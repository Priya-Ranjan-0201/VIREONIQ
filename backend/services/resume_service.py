import uuid
import os
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from services import resume_parser, resume_scorer
from crud import crud_resume
from db.models import User

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

os.makedirs(UPLOAD_DIR, exist_ok=True)

import magic

async def process_and_score_resume(
    db: AsyncSession, 
    file: UploadFile, 
    target_role: str, 
    current_user: User
) -> list:
    """
    Read file bytes, validate size and MIME type with python-magic,
    extract text sections, and calculate resume evaluation score.
    """
    # 1. Read bytes for validation
    file_bytes = await file.read()
    
    # 2. Size Validation
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="File size exceeds the 5MB limit."
        )
        
    # 3. MIME Validation via python-magic on raw bytes
    detected_mime = magic.from_buffer(file_bytes, mime=True)
    allowed_mimes = [
        "application/pdf", 
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    if detected_mime not in allowed_mimes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Only PDF and DOCX files are allowed."
        )
        
    # 4. Store Securely (Local mock for S3/R2)
    storage_key = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, storage_key)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
        
    # 5. Parse Text
    try:
        if detected_mime == "application/pdf":
            raw_text = resume_parser.parse_pdf(file_bytes)
        else:
            raw_text = resume_parser.parse_docx(file_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Failed to parse document: {str(e)}"
        )

    # 6. Extract Sections
    sections = resume_parser.extract_sections(raw_text)
    
    # 6b. Get page count and validate if it resembles a resume
    page_count = resume_parser.get_page_count(file_bytes, detected_mime)
    if not resume_parser.is_valid_resume(sections, raw_text, page_count):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded document does not appear to be a valid resume/CV. Please upload a PDF or DOCX file containing relevant details (such as experience, education, projects, or skills)."
        )
        
    # Save base resume
    resume_obj = await crud_resume.create_resume(
        db, 
        user_id=current_user.id, 
        storage_key=storage_key, 
        mime_type=detected_mime, 
        parsed_data=sections
    )

    
    # 6. Score & Extract NLP Entities
    scores, entities = resume_scorer.analyze_resume(sections, target_role)
    
    # Save scores and entities
    await crud_resume.create_resume_score(db, resume_id=resume_obj.id, scores=scores)
    await crud_resume.create_resume_entities(db, resume_id=resume_obj.id, entities=entities)
    
    # Refresh to load relationships
    return await crud_resume.get_user_resumes(db, current_user.id)
