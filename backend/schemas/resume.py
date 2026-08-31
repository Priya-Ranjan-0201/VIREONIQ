from typing import Optional, List, Dict, Any
from pydantic import BaseModel, UUID4
from datetime import datetime

class ResumeScoreResponse(BaseModel):
    id: UUID4
    overall_score: float
    keyword_match_score: Optional[float]
    completeness_score: Optional[float]
    quantified_achievements_score: Optional[float]
    action_verb_score: Optional[float]
    formatting_score: Optional[float]
    role_relevance_score: Optional[float]
    improvement_notes: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True

class ResumeUploadResponse(BaseModel):
    id: UUID4
    storage_key: str
    is_active: bool
    scores: List[ResumeScoreResponse] = []
    
    class Config:
        from_attributes = True

class ResumeHistoryResponse(BaseModel):
    resumes: List[ResumeUploadResponse]
