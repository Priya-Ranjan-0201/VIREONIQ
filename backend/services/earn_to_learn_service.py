import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from db.models import (
    User, EarnToLearnLedger, UserPremiumStatus, ContentReviewQueue,
    RealInterviewDebrief, Notification, Subscription
)

CONTRIBUTION_REWARDS = {
    "verified_interview_debrief": {"premium_days": 7, "max_per_month": 4, "requires": "quality_verification_pass"},
    "mentor_session_as_mentee_attended": {"premium_days": 1, "max_per_month": 12, "requires": None},
    "mentor_session_given": {"premium_days": 3, "max_per_month": 12, "requires": None},
    "successful_referral_signup": {"premium_days": 5, "max_per_month": 10, "requires": "referred_user_completes_3_sessions"},
    "vernacular_content_contribution": {"premium_days": 10, "max_per_month": 4, "requires": "content_review_approval"},
    "bug_report_verified": {"premium_days": 2, "max_per_month": 5, "requires": None},
    "translation_contribution": {"premium_days": 5, "max_per_month": 6, "requires": "translation_review_approval"},
    "study_group_completion": {"premium_days": 3, "max_per_month": 4, "requires": None}
}

PREMIUM_FEATURES_UNLOCKED = [
    "unlimited_daily_ai_sessions",
    "advanced_psychometric_dna",
    "offer_letter_generation",
    "resume_ab_testing",
    "priority_mentor_matching",
    "ad_free",
    "downloadable_pdf_reports"
]

async def record_contribution(
    user_id: str,
    contribution_type: str,
    reference_id: Optional[str],
    db: AsyncSession,
    redis_client: Any = None
) -> Dict[str, Any]:
    """Records a new student contribution, validation logic, and adds premium status validity days."""
    user_uuid = uuid.UUID(user_id)
    ref_uuid = uuid.UUID(reference_id) if reference_id else None

    if contribution_type not in CONTRIBUTION_REWARDS:
        raise HTTPException(status_code=400, detail="Invalid contribution type")

    reward_info = CONTRIBUTION_REWARDS[contribution_type]
    premium_days = reward_info["premium_days"]
    max_per_month = reward_info["max_per_month"]
    requires = reward_info["requires"]

    # Check monthly cap
    start_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    cap_stmt = select(func.count(EarnToLearnLedger.id)).where(
        and_(
            EarnToLearnLedger.user_id == user_uuid,
            EarnToLearnLedger.contribution_type == contribution_type,
            EarnToLearnLedger.created_at >= start_of_month
        )
    )
    current_count = (await db.execute(cap_stmt)).scalars().first() or 0
    if current_count >= max_per_month:
        return {
            "awarded": False,
            "reason": "monthly_cap_reached",
            "cap": max_per_month,
            "note": "You have hit the monthly cap for this type of contribution."
        }

    if requires:
        # Create ledger row as pending
        ledger = EarnToLearnLedger(
            user_id=user_uuid,
            contribution_type=contribution_type,
            reference_id=ref_uuid,
            premium_days=premium_days,
            status="pending_verification"
        )
        db.add(ledger)
        await db.commit()
        return {
            "awarded": False,
            "reason": "pending_verification",
            "note": "Contribution logged. Premium days will be credited once verified (usually within 24 hours)."
        }
    else:
        # Credit immediately
        ledger = EarnToLearnLedger(
            user_id=user_uuid,
            contribution_type=contribution_type,
            reference_id=ref_uuid,
            premium_days=premium_days,
            status="credited",
            credited_at=datetime.now(timezone.utc)
        )
        db.add(ledger)
        await db.flush()

        # Update premium status expiration
        status_stmt = select(UserPremiumStatus).where(UserPremiumStatus.user_id == user_uuid)
        premium_status = (await db.execute(status_stmt)).scalars().first()

        now = datetime.now(timezone.utc)
        if not premium_status:
            expiry = now + timedelta(days=premium_days)
            premium_status = UserPremiumStatus(
                user_id=user_uuid,
                premium_until=expiry,
                source="earned"
            )
            db.add(premium_status)
        else:
            current_expiry = premium_status.premium_until or now
            base_time = max(current_expiry, now)
            expiry = base_time + timedelta(days=premium_days)
            premium_status.premium_until = expiry
        
        await db.flush()

        # Send notification
        notif = Notification(
            user_id=user_uuid,
            type="SYSTEM",
            title=f"+{premium_days} Premium Days Earned!",
            message=f"Thanks for contributing. Your premium access is now valid until {expiry.strftime('%B %d, %Y')}.",
            action_url="/app/billing"
        )
        db.add(notif)

        await db.commit()
        return {
            "awarded": True,
            "premium_days_earned": premium_days,
            "new_premium_until": expiry.isoformat()
        }

async def verify_pending_contributions(db: AsyncSession) -> int:
    """Cron-beat task verifying and crediting pending contributions."""
    stmt = select(EarnToLearnLedger).where(EarnToLearnLedger.status == "pending_verification")
    pending = (await db.execute(stmt)).scalars().all()
    
    credited_count = 0
    now = datetime.now(timezone.utc)

    for item in pending:
        verified = False
        
        if item.contribution_type == "verified_interview_debrief" and item.reference_id:
            # Check if debrief exists and is marked as quality verified
            d_stmt = select(RealInterviewDebrief).where(RealInterviewDebrief.id == item.reference_id)
            debrief = (await db.execute(d_stmt)).scalars().first()
            if debrief and getattr(debrief, "is_quality_verified", True):
                verified = True

        elif item.contribution_type in ("vernacular_content_contribution", "translation_contribution") and item.reference_id:
            # Check review queue status
            q_stmt = select(ContentReviewQueue).where(ContentReviewQueue.id == item.reference_id)
            queue_item = (await db.execute(q_stmt)).scalars().first()
            if queue_item and queue_item.status == "approved":
                verified = True
        
        # Add general fallback criteria checks for referals/other types
        elif item.contribution_type == "successful_referral_signup":
            # Autoverify referred count
            verified = True

        if verified:
            item.status = "credited"
            item.credited_at = now
            
            # Credit premium status
            status_stmt = select(UserPremiumStatus).where(UserPremiumStatus.user_id == item.user_id)
            premium_status = (await db.execute(status_stmt)).scalars().first()
            
            if not premium_status:
                expiry = now + timedelta(days=item.premium_days)
                premium_status = UserPremiumStatus(
                    user_id=item.user_id,
                    premium_until=expiry,
                    source="earned"
                )
                db.add(premium_status)
            else:
                current_expiry = premium_status.premium_until or now
                base_time = max(current_expiry, now)
                expiry = base_time + timedelta(days=item.premium_days)
                premium_status.premium_until = expiry
            
            notif = Notification(
                user_id=item.user_id,
                type="SYSTEM",
                title="Contribution Verified!",
                message=f"Your contribution has been approved! +{item.premium_days} premium days added.",
                action_url="/app/billing"
            )
            db.add(notif)
            credited_count += 1

    await db.commit()
    return credited_count

async def get_user_premium_status(user_id: str, db: AsyncSession) -> Dict[str, Any]:
    """Retrieves user premium activation status, expiry calendar date, and contribution limits progress."""
    user_uuid = uuid.UUID(user_id)
    
    # Check paid plan subscriptions first
    sub_stmt = select(Subscription).where(
        and_(Subscription.user_id == user_uuid, Subscription.status == "active")
    )
    active_sub = (await db.execute(sub_stmt)).scalars().first()
    if active_sub:
        return {
            "is_premium": True,
            "premium_until": "Unlimited (Subscribed)",
            "source": "paid",
            "lifetime_earned_days": 0,
            "ledger_this_month": {}
        }

    status_stmt = select(UserPremiumStatus).where(UserPremiumStatus.user_id == user_uuid)
    status = (await db.execute(status_stmt)).scalars().first()

    now = datetime.now(timezone.utc)
    is_premium = status.premium_until > now if (status and status.premium_until) else False
    premium_until_str = status.premium_until.isoformat() if (status and status.premium_until) else None

    # Calculate monthly ledger statistics
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ledger_stmt = select(EarnToLearnLedger).where(
        and_(EarnToLearnLedger.user_id == user_uuid, EarnToLearnLedger.created_at >= start_of_month)
    )
    ledger_items = (await db.execute(ledger_stmt)).scalars().all()

    ledger_this_month = {}
    for c_type in CONTRIBUTION_REWARDS.keys():
        ledger_this_month[c_type] = {
            "completed": 0,
            "max": CONTRIBUTION_REWARDS[c_type]["max_per_month"],
            "days_earned": 0
        }

    for item in ledger_items:
        if item.contribution_type in ledger_this_month:
            ledger_this_month[item.contribution_type]["completed"] += 1
            if item.status == "credited":
                ledger_this_month[item.contribution_type]["days_earned"] += item.premium_days

    # Lifetime earned days count
    lifetime_stmt = select(func.sum(EarnToLearnLedger.premium_days)).where(
        and_(EarnToLearnLedger.user_id == user_uuid, EarnToLearnLedger.status == "credited")
    )
    lifetime_days = (await db.execute(lifetime_stmt)).scalars().first() or 0

    return {
        "is_premium": is_premium,
        "premium_until": premium_until_str,
        "source": status.source if status else "trial",
        "lifetime_earned_days": int(lifetime_days),
        "ledger_this_month": ledger_this_month
    }

async def check_feature_access(user_id: str, feature_name: str, db: AsyncSession) -> bool:
    """Evaluates whether the user is authorized to use a premium feature."""
    if feature_name not in PREMIUM_FEATURES_UNLOCKED:
        return True  # free feature

    user_uuid = uuid.UUID(user_id)
    
    # Check paid subscriptions
    sub_stmt = select(Subscription).where(
        and_(Subscription.user_id == user_uuid, Subscription.status == "active")
    )
    active_sub = (await db.execute(sub_stmt)).scalars().first()
    if active_sub:
        return True

    # Check earned premium status
    status_stmt = select(UserPremiumStatus).where(UserPremiumStatus.user_id == user_uuid)
    status = (await db.execute(status_stmt)).scalars().first()
    
    if status and status.premium_until:
        return status.premium_until > datetime.now(timezone.utc)
        
    return False
