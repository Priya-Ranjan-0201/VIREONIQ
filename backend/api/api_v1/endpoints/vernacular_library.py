from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any

from api import deps
from db.session import get_db
from db.models import User
from services import vernacular_library_service

router = APIRouter()

@router.get("/concepts", response_model=List[Dict[str, Any]])
async def list_vernacular_concepts_query(
    language: str = "hi",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> List[Dict[str, Any]]:
    """Lists all programming concepts with native-language translations via query param."""
    return await vernacular_library_service.get_concepts_by_language(
        language=language,
        db=db
    )

@router.get("/concepts/{language}", response_model=List[Dict[str, Any]])
async def list_vernacular_concepts(
    language: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> List[Dict[str, Any]]:
    """Lists all programming concepts with native-language translations and analogical references."""
    concepts = await vernacular_library_service.get_concepts_by_language(
        language=language,
        db=db
    )
    return concepts

@router.get("/concepts/{language}/{concept_key}", response_model=Dict[str, Any])
async def get_vernacular_concept_detail(
    language: str,
    concept_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Retrieves standard syntax descriptions and local analogies for a single concept."""
    detail = await vernacular_library_service.get_concept_details(
        language=language,
        concept_key=concept_key,
        db=db
    )
    return detail
