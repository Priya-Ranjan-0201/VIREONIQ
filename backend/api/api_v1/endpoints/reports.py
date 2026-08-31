from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from db.models import User
from api import deps
from services import report_service

router = APIRouter()

@router.get("/benchmark")
async def get_benchmark_report(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a detailed benchmark report comparing the user to the global talent pool.
    """
    return await report_service.generate_benchmark_report(db, current_user.id)


from fastapi.responses import Response
from services import pdf_export

@router.post("/export-pdf")
async def export_gap_report_pdf(
    role_name: str = "Software Engineer",
    company_name: str = "Google",
    ctc: float = 24.5,
    current_user: User = Depends(deps.get_current_active_user)
) -> Response:
    """
    Export the placement readiness gap report or mock offer letter as a PDF download.
    """
    student_name = f"{current_user.email.split('@')[0]}"
    pdf_bytes = pdf_export.generate_offer_letter_pdf(
        student_name=student_name,
        company_name=company_name,
        role_name=role_name,
        ctc=ctc
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=vireoniq_report.pdf"}
    )
