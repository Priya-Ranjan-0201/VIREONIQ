import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from db.models import (
    User, Profile, StudentProfile, ParentLink, InterviewSession,
    GamificationProfile, Notification
)

async def request_parent_consent(
    student_user_id: str,
    parent_phone: str,
    parent_name: str,
    db: AsyncSession
) -> ParentLink:
    """Initiates parent link record in pending state and alerts student to approve."""
    student_uuid = uuid.UUID(student_user_id)

    # Validate parent_phone format (simple length check)
    if len(parent_phone) < 8:
        raise HTTPException(status_code=400, detail="Invalid parent phone number format")

    # Create link request
    link = ParentLink(
        student_id=student_uuid,
        parent_phone=parent_phone,
        parent_name=parent_name,
        consent_status="pending",
        consent_requested_at=datetime.now(timezone.utc)
    )
    db.add(link)
    await db.flush()

    # Send in-app notification to student asking for confirmation
    notif = Notification(
        user_id=student_uuid,
        type="NUDGE",
        title="Confirm parent progress updates",
        message=f"You have requested to share weekly updates with {parent_name} ({parent_phone}). Click to confirm consent.",
        action_url="/app/parent-connect"
    )
    db.add(notif)
    
    await db.commit()
    return link

async def confirm_parent_link(
    student_user_id: str,
    parent_link_id: str,
    db: AsyncSession
) -> None:
    """Verifies student consent, activates parent updates, and dispatches mock WhatsApp welcoming."""
    student_uuid = uuid.UUID(student_user_id)
    link_uuid = uuid.UUID(parent_link_id)

    stmt = select(ParentLink).where(and_(ParentLink.id == link_uuid, ParentLink.student_id == student_uuid))
    link = (await db.execute(stmt)).scalars().first()
    if not link:
        raise HTTPException(status_code=404, detail="Parent connection request not found")

    link.consent_status = "active"
    link.consented_at = datetime.now(timezone.utc)
    
    # Fetch student name
    s_stmt = select(Profile).where(Profile.user_id == student_uuid)
    student_profile = (await db.execute(s_stmt)).scalars().first()
    student_name = student_profile.first_name if student_profile else "Student"

    # Send Welcome WhatsApp Mock
    # In production, this would trigger a Twilio WhatsApp message
    print(
        f"[MOCK WHATSAPP] To: {link.parent_phone}\n"
        f"Hi {link.parent_name}, this is PlaceIQ. {student_name} has added you to "
        f"receive a simple weekly update on their placement preparation progress. "
        f"You'll get one message every Sunday. Reply STOP anytime to opt out."
    )

    await db.commit()

async def revoke_parent_consent(
    student_user_id: str,
    parent_link_id: str,
    db: AsyncSession
) -> None:
    """Revokes consent and sends final opt-out WhatsApp message."""
    student_uuid = uuid.UUID(student_user_id)
    link_uuid = uuid.UUID(parent_link_id)

    stmt = select(ParentLink).where(and_(ParentLink.id == link_uuid, ParentLink.student_id == student_uuid))
    link = (await db.execute(stmt)).scalars().first()
    if not link:
        raise HTTPException(status_code=404, detail="Parent connection not found")

    link.consent_status = "revoked"
    link.revoked_at = datetime.now(timezone.utc)

    # Send Unsubscribe WhatsApp Mock
    print(
        f"[MOCK WHATSAPP] To: {link.parent_phone}\n"
        f"Weekly updates have been turned off as requested. Thank you for supporting their preparation journey."
    )

    await db.commit()

async def generate_weekly_parent_message(
    student_user_id: str,
    parent_name: str,
    db: AsyncSession
) -> str:
    """Aggregates student metrics (streak, badges, mock count) into a warm progress note."""
    student_uuid = uuid.UUID(student_user_id)

    # Fetch student profile name
    s_stmt = select(Profile).where(Profile.user_id == student_uuid)
    student_profile = (await db.execute(s_stmt)).scalars().first()
    student_name = student_profile.first_name if student_profile else "Student"
    prs_score = float(student_profile.placement_readiness_score) if student_profile else 0.0

    # Fetch interview counts this week
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    sess_stmt = select(InterviewSession).where(
        and_(InterviewSession.user_id == student_uuid, InterviewSession.ended_at >= one_week_ago)
    )
    sessions_this_week = len((await db.execute(sess_stmt)).scalars().all())

    # Fetch streak
    g_stmt = select(GamificationProfile).where(GamificationProfile.user_id == student_uuid)
    gam_profile = (await db.execute(g_stmt)).scalars().first()
    
    current_streak = 0
    if gam_profile and hasattr(gam_profile, 'streaks'):
        current_streak = getattr(gam_profile, 'streaks', 0)
    elif gam_profile:
        # fallback
        current_streak = int((gam_profile.total_xp or 0) / 100)

    # Compose progress note
    if sessions_this_week > 0:
        msg = (
            f"Hi {parent_name}! Weekly update for {student_name}:\n\n"
            f"📊 Practiced {sessions_this_week} times this week\n"
            f"📈 Placement readiness is currently at {prs_score}%\n"
            f"🔥 {current_streak}-day practice streak\n\n"
            f"They're putting in the work. A small word of encouragement from you goes a long way."
        )
    else:
        msg = (
            f"Hi {parent_name}! Weekly update for {student_name}:\n\n"
            f"No practice sessions logged this week.\n\n"
            f"A gentle check-in from you (not pressure — just interest) often helps more than you'd expect."
        )

    return msg
