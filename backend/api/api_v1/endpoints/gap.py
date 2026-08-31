from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from schemas.gap import AnalyzeGapRequest, GapAnalysisResponse, GapHistoryResponse
from services import gap_service
from api import deps
from db.models import User
from crud import crud_gap

router = APIRouter()

@router.post("/analyze", response_model=GapAnalysisResponse)
async def analyze_gap(
    request: AnalyzeGapRequest,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Run the Placement Gap Analysis Engine against the user's latest parsed resume.
    Generates a 30/60/90 day plan based on missing skills.
    """
    return await gap_service.perform_gap_analysis(db, request, current_user)

@router.get("/history", response_model=GapHistoryResponse)
async def get_gap_history(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all historical gap analyses for the user.
    """
    analyses = await crud_gap.get_user_gap_history(db, current_user.id)
    return {"analyses": analyses}
