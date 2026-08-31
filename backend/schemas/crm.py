from typing import List, Optional
from pydantic import BaseModel, UUID4
from datetime import datetime

# --- Application Events ---
class ApplicationEventBase(BaseModel):
    event_type: str # Interview Scheduled, OA Received, etc.
    event_date: datetime
    notes: Optional[str] = None

class ApplicationEventCreate(ApplicationEventBase):
    application_id: str

class ApplicationEventResponse(ApplicationEventBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

# --- Offers ---
class OfferBase(BaseModel):
    base_salary: float
    currency: str = "INR"
    bonus: Optional[float] = 0
    equity_text: Optional[str] = None
    location: Optional[str] = None
    deadline: Optional[datetime] = None
    notes: Optional[str] = None

class OfferCreate(OfferBase):
    application_id: str

class OfferResponse(OfferBase):
    id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

# --- Applications ---
class ApplicationBase(BaseModel):
    job_id: str
    status: str = "saved"
    is_referral: bool = False
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    stage_id: Optional[int] = None
    notes: Optional[str] = None
    rejection_reason: Optional[str] = None

class ApplicationResponse(ApplicationBase):
    id: str
    stage_id: int
    applied_at: datetime
    updated_at: datetime
    events: List[ApplicationEventResponse] = []
    offer: Optional[OfferResponse] = None

    class Config:
        from_attributes = True

# --- Analytics ---
class FunnelStats(BaseModel):
    stage: str
    count: int
    conversion_rate: float
