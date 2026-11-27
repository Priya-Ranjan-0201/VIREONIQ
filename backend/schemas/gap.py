from typing import Optional, List
from pydantic import BaseModel, UUID4, Field
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
    # placement_probability is a deprecated heuristic proxy; replaced with readiness_estimate_heuristic
    placement_probability: Optional[float] = Field(
        default=None,
        description="Deprecated heuristic readiness proxy (0-100); see readiness_estimate_heuristic"
    )
    readiness_estimate_heuristic: Optional[float] = Field(
        default=None,
        description="Heuristic skill-fit readiness benchmark (not a hiring guarantee or real placement prediction)"
    )
    uncertainty_range: Optional[str] = Field(
        default=None,
        description="Estimated uncertainty interval for the heuristic score"
    )
    expected_salary_band: Optional[str] = None
    
    recommendations: List[GapRecommendationSchema] = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class GapHistoryResponse(BaseModel):
    analyses: List[GapAnalysisResponse]
