from typing import Optional, List
from pydantic import BaseModel, UUID4
from datetime import datetime

class AnalyzeGapRequest(BaseModel):
    target_role: str
    company_type: str
    experience_level_years: Optional[float] = 0.0

class GapRecommendationSchema(BaseModel):
    id: UUID4
    time_horizon_days: int
    dimension: Optional[str] = None
    task_description: str
    resources: Optional[list] = None
    is_completed: bool

    class Config:
        from_attributes = True

class GapAnalysisResponse(BaseModel):
    id: UUID4
    target_role_name: str
    company_type: Optional[str] = None
    
    technical_gap_score: Optional[float] = None
    communication_gap_score: Optional[float] = None
    project_gap_score: Optional[float] = None
    confidence_gap_score: Optional[float] = None
    consistency_gap_score: Optional[float] = None
    overall_readiness_score: Optional[float] = None
    
    technical_gap_severity: Optional[str] = None
    communication_gap_severity: Optional[str] = None
    project_gap_severity: Optional[str] = None
    confidence_gap_severity: Optional[str] = None
    consistency_gap_severity: Optional[str] = None
    
    missing_skills: Optional[List[str]] = None
    placement_probability: Optional[float] = None
    expected_salary_band: Optional[str] = None
    
    recommendations: List[GapRecommendationSchema] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class GapHistoryResponse(BaseModel):
    analyses: List[GapAnalysisResponse]

