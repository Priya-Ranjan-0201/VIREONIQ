from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from db.session import get_db
from db.models import User, Notification, Reminder
from schemas.notification import NotificationResponse, ReminderResponse, ReminderCreate
from api import deps

router = APIRouter()

@router.get("", response_model=List[NotificationResponse])
@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 20
):
    """Get latest notifications for the current user."""
    result = await db.execute(
        select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(limit)
    )
    return result.scalars().all()

@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a notification as read."""
    await db.execute(
        update(Notification).where(and_(Notification.id == notification_id, Notification.user_id == current_user.id)).values(is_read=True)
    )
    await db.commit()
    return {"status": "success"}

@router.get("/reminders", response_model=List[ReminderResponse])
async def get_reminders(
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get active reminders for the current user."""
    result = await db.execute(
        select(Reminder).where(and_(Reminder.user_id == current_user.id, Reminder.is_completed == False)).order_by(Reminder.remind_at.asc())
    )
    return result.scalars().all()

@router.post("/reminders", response_model=ReminderResponse)
async def create_reminder(
    reminder_in: ReminderCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Manually create a reminder."""
    reminder = Reminder(
        user_id=current_user.id,
        **reminder_in.model_dump()
    )
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    return reminder
