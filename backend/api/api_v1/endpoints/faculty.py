from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from sqlalchemy import select, func

from api import deps
from db.session import get_db
from db.models import User, FacultyClass, FacultyClassStudent
from services import faculty_service

router = APIRouter()

@router.post("/classes", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_class(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_faculty_or_admin)
) -> Dict[str, Any]:
    """Faculty creates a new classroom cohort with subject topics and student email invitations."""
    class_name = payload.get("class_name")
    subject_topics = payload.get("subject_topics", [])
    student_emails = payload.get("student_emails", [])
    
    if not class_name:
        raise HTTPException(status_code=400, detail="class_name is required")

    class_obj = await faculty_service.create_faculty_class(
        faculty_user_id=str(current_user.id),
        class_name=class_name,
        subject_topics=subject_topics,
        student_emails=student_emails,
        db=db
    )
    return {
        "class_id": str(class_obj.id),
        "class_name": class_obj.class_name,
        "join_code": class_obj.join_code,
        "student_count": class_obj.student_count
    }

@router.get("/classes", response_model=List[Dict[str, Any]])
async def list_classes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_faculty_or_admin)
) -> List[Dict[str, Any]]:
    """Lists all classrooms created by the authenticated faculty member."""
    stmt = select(FacultyClass).where(FacultyClass.faculty_id == current_user.id)
    classes = (await db.execute(stmt)).scalars().all()
    
    return [
        {
            "class_id": str(c.id),
            "class_name": c.class_name,
            "join_code": c.join_code,
            "student_count": c.student_count,
            "subject_topics": c.subject_topics,
            "created_at": c.created_at.isoformat()
        }
        for c in classes
    ]

@router.post("/classes/join", response_model=Dict[str, Any])
async def student_join_class(
    payload: Dict[str, str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Allows a student user to self-enroll in a faculty class using a join code."""
    join_code = payload.get("join_code")
    if not join_code:
        raise HTTPException(status_code=400, detail="join_code is required")

    # Find class by join code
    stmt = select(FacultyClass).where(FacultyClass.join_code == join_code)
    cls = (await db.execute(stmt)).scalars().first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class join code invalid")

    # Check if student is already linked
    link_stmt = select(FacultyClassStudent).where(
        FacultyClassStudent.class_id == cls.id,
        FacultyClassStudent.student_id == current_user.id
    )
    link = (await db.execute(link_stmt)).scalars().first()
    
    if link:
        if link.status == "linked":
            return {"status": "already_joined", "class_name": cls.class_name}
        link.status = "linked"
        link.linked_at = func.now()
    else:
        # Check if student email was pending
        email_stmt = select(FacultyClassStudent).where(
            FacultyClassStudent.class_id == cls.id,
            func.lower(FacultyClassStudent.pending_email) == func.lower(current_user.email)
        )
        link = (await db.execute(email_stmt)).scalars().first()
        if link:
            link.student_id = current_user.id
            link.status = "linked"
            link.linked_at = func.now()
        else:
            link = FacultyClassStudent(
                class_id=cls.id,
                student_id=current_user.id,
                pending_email=current_user.email,
                status="linked",
                linked_at=func.now()
            )
            db.add(link)

    cls.student_count += 1
    await db.commit()
    return {"status": "joined", "class_name": cls.class_name}

@router.get("/classes/{id}/overview", response_model=Dict[str, Any])
async def get_class_overview(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_faculty_or_admin)
) -> Dict[str, Any]:
    """Fetches aggregated statistics and risk logs for a classroom cohort."""
    overview = await faculty_service.get_class_readiness_overview(
        class_id=id,
        faculty_user_id=str(current_user.id),
        db=db
    )
    return overview

@router.get("/classes/{id}/students/{student_id}", response_model=Dict[str, Any])
async def get_student_details(
    id: str,
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_faculty_or_admin)
) -> Dict[str, Any]:
    """Fetches anonymized performance analytics and coaching prompts for a specific student."""
    student_summary = await faculty_service.get_individual_student_summary(
        class_id=id,
        student_user_id=student_id,
        faculty_user_id=str(current_user.id),
        db=db
    )
    return student_summary

@router.post("/classes/{id}/students/{student_id}/nudge", status_code=status.HTTP_200_OK)
async def nudge_student(
    id: str,
    student_id: str,
    payload: Dict[str, str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_faculty_or_admin)
) -> Dict[str, str]:
    """Sends a placement nudge or reminder directly to the student."""
    message = payload.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="message text is required")

    await faculty_service.send_intervention_nudge(
        class_id=id,
        student_user_id=student_id,
        faculty_user_id=str(current_user.id),
        custom_message=message,
        db=db
    )
    return {"status": "nudge_sent"}
