from typing import Optional, List, Dict, Any
from pydantic import BaseModel, UUID4
from datetime import datetime

class InterviewStartRequest(BaseModel):
    target_role: str
    difficulty_level: float = 1.0 # 1.0 to 5.0
    session_mode: str = "practice" # practice or assessment

class InterviewAnswerSchema(BaseModel):
    turn_number: int
    question_text: str
    answer_text: Optional[str]
    ai_evaluation: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True

class InterviewScoreSchema(BaseModel):
    technical_correctness: float
    communication_clarity: float
    confidence_tone: float
    completeness: float
    feedback_summary: str

    class Config:
        from_attributes = True

class InterviewSessionResponse(BaseModel):
    id: UUID4
    target_role: str
    difficulty_level: float
    session_mode: str
    status: str
    started_at: datetime
    current_question: Optional[str] = None
    turn_number: int = 1
    
    class Config:
        from_attributes = True

class AnswerSubmission(BaseModel):
    answer_text: str

class InterviewScorecard(BaseModel):
    session_id: UUID4
    overall_score: Optional[float]
    score_breakdown: Optional[InterviewScoreSchema]
    answers: List[InterviewAnswerSchema]

    class Config:
        from_attributes = True
