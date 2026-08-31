from typing import List, Optional
from pydantic import BaseModel, UUID4
from datetime import datetime

class NotificationBase(BaseModel):
    type: str # INTERVIEW, OFFER, SYSTEM, NUDGE
    title: str
    message: str
    action_url: Optional[str] = None

class NotificationResponse(NotificationBase):
    id: UUID4
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ReminderBase(BaseModel):
    title: str
    message: Optional[str] = None
    remind_at: datetime

class ReminderCreate(ReminderBase):
    application_id: Optional[str] = None

class ReminderResponse(ReminderBase):
    id: UUID4
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True
