from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from datetime import datetime

# Job Listings
class JobListingBase(BaseModel):
    title: str
    company_name: str
    company_tier: str # Product, Startup, Service
    description: str
    required_skills: str
    location: str
    salary_min: Optional[float]
    salary_max: Optional[float]
    is_remote: bool = False
    job_type: str # Full-time, Internship, Contract
    source_url: Optional[str]

class JobListingCreate(JobListingBase):
    pass

class JobListingResponse(JobListingBase):
    id: str
    source: str
    posted_at: datetime
    competition_index: float
    language_support: str
    created_at: datetime

    class Config:
        from_attributes = True

# User Preferences
class UserPreferenceBase(BaseModel):
    target_roles: List[str]
    preferred_locations: List[str]
    min_salary_target: float
    remote_only: bool = False
    experience_level: str # Entry, Mid, Senior

class UserPreferenceUpdate(UserPreferenceBase):
    pass

class UserPreferenceResponse(UserPreferenceBase):
    user_id: str

    class Config:
        from_attributes = True

# Recommendations & Matching
class MatchExplanation(BaseModel):
    reasons: List[str]
    missing_blockers: List[str]

class JobMatchResponse(BaseModel):
    job: JobListingResponse
    match_score: float
    skill_fit_score: float
    offer_probability_score: float
    confidence_level: str # Low, Medium, High
    explanation: MatchExplanation
    salary_band: str
    ai_feedback: Optional[str] = None

class RecommendationStats(BaseModel):
    overall_employability_index: float
    market_worth_estimate: str
    top_skill_gaps: List[str]
    weekly_targets: List[str]
