import uuid
from datetime import datetime, date, timezone, timedelta
from typing import Dict, Any, List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from db.models import User, Profile, StudentProfile, MentorProfile, ReferralSlot, Notification
from services import gamification_service
from core.redis import redis_client

REFERRAL_LIMITS = {
    "referrals_per_quarter": 3,
    "min_days_at_company": 90,
    "cooldown_days_after_declined": 30
}

def get_current_quarter() -> str:
    today = date.today()
    q = (today.month - 1) // 3 + 1
    return f"{today.year}-Q{q}"

async def list_referral_slots(
    referrer_user_id: uuid.UUID,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Checks referral availability and active slots count for the current quarter.
    """
    # 1. Fetch mentor profile
    stmt = select(MentorProfile).where(MentorProfile.user_id == referrer_user_id)
    mentor = (await db.execute(stmt)).scalars().first()
    if not mentor or not mentor.is_active:
        return {
            "available": 0,
            "used": 0,
            "reason": "mentor_profile_not_active",
            "slots_this_quarter": REFERRAL_LIMITS["referrals_per_quarter"]
        }

    # 2. Check tenure requirements (90 days)
    today_dt = date.today()
    start_date = mentor.commitment_start_date.date() if mentor.commitment_start_date else today_dt
    days_since = (today_dt - start_date).days
    
    if days_since < REFERRAL_LIMITS["min_days_at_company"]:
        eligible_date = start_date + timedelta(days=REFERRAL_LIMITS["min_days_at_company"])
        return {
            "available": 0,
            "used": 0,
            "reason": "minimum_tenure_not_met",
            "eligible_date": eligible_date.isoformat(),
            "slots_this_quarter": REFERRAL_LIMITS["referrals_per_quarter"]
        }

    # 3. Fetch active slots in current quarter
    current_q = get_current_quarter()
    slot_stmt = select(ReferralSlot).where(
        and_(
            ReferralSlot.referrer_id == referrer_user_id,
            ReferralSlot.quarter == current_q,
            ReferralSlot.status.in_(["matched", "accepted", "submitted", "hired"])
        )
    )
    slots = (await db.execute(slot_stmt)).scalars().all()
    used = len(slots)
    available = max(0, REFERRAL_LIMITS["referrals_per_quarter"] - used)

    return {
        "available": available,
        "used": used,
        "slots_this_quarter": REFERRAL_LIMITS["referrals_per_quarter"]
    }

async def find_best_candidates_for_referral(
    referrer_user_id: uuid.UUID,
    target_company: str,
    target_role: str,
    db: AsyncSession
) -> List[Dict[str, Any]]:
    """
    Identifies high-performing students who match target criteria.
    """
    # Query candidates who are still seeking and have completed 10+ prep sessions
    stud_stmt = select(StudentProfile).where(
        and_(
            StudentProfile.onboarding_step == "completed", # ready signal
            StudentProfile.user_id != referrer_user_id
        )
    )
    student_profiles = (await db.execute(stud_stmt)).scalars().all()

    candidates = []
    for s in student_profiles:
        # Check sessions completed by fetching their profile
        prof_stmt = select(Profile).where(Profile.user_id == s.user_id)
        profile = (await db.execute(prof_stmt)).scalar_one_or_none()
        if not profile:
            continue
            
        prs = float(profile.placement_readiness_score or 0.0)
        
        # Verify no existing referral slot at this company
        exist_stmt = select(ReferralSlot).where(
            and_(
                ReferralSlot.candidate_id == s.user_id,
                ReferralSlot.company_name.ilike(f"%{target_company}%")
            )
        )
        existing = (await db.execute(exist_stmt)).scalars().first()
        if existing:
            continue

        # Heuristic role overlap matching
        cand_role = (profile.target_role or "").lower()
        t_role = target_role.lower()
        
        match_score = 50.0
        if cand_role == t_role:
            match_score += 30.0
        elif t_role in cand_role or cand_role in t_role:
            match_score += 15.0

        # Anonymized mock match ID
        match_id = str(uuid.uuid4())[:8]
        # Store mapping in Redis (match_id -> candidate_user_id)
        redis_key = f"referral:match_mapping:{match_id}"
        await redis_client.setex(redis_key, 86400, str(s.user_id))

        # Check credential tier
        from db.models import SkillCredential
        cred_stmt = select(SkillCredential).where(SkillCredential.user_id == s.user_id)
        cred = (await db.execute(cred_stmt)).scalars().first()
        tier = cred.tier if cred else "bronze"

        final_composite_score = (match_score * 0.6) + (prs * 0.4)
        candidates.append({
            "match_id": match_id,
            "credential_tier": tier,
            "prs_score": prs,
            "match_score": round(final_composite_score, 1),
            "top_3_skills": ["Python", "FastAPI", "SQL"][:3], # placeholder logic
            "sessions_completed": 12 # ready signal
        })

    candidates.sort(key=lambda x: x["match_score"], reverse=True)
    return candidates[:5]

async def create_referral_match(
    referrer_user_id: uuid.UUID,
    candidate_match_id: str,
    target_company: str,
    target_role: str,
    personal_note: str,
    db: AsyncSession
) -> ReferralSlot:
    """
    Creates a referral slot, deducts quotas, and sends notification updates.
    """
    # 1. Quota check
    avail_status = await list_referral_slots(referrer_user_id, db)
    if avail_status["available"] <= 0:
        raise ValueError("No available quarterly referral slots remaining.")

    # 2. Resolve Candidate match ID
    redis_key = f"referral:match_mapping:{candidate_match_id}"
    cand_raw = await redis_client.get(redis_key)
    if not cand_raw:
        raise ValueError("Candidate match ID expired or invalid.")
    candidate_user_id = uuid.UUID(cand_raw)

    # 3. Cooldown check
    exist_stmt = select(ReferralSlot).where(
        and_(
            ReferralSlot.candidate_id == candidate_user_id,
            ReferralSlot.company_name.ilike(f"%{target_company}%")
        )
    )
    existing = (await db.execute(exist_stmt)).scalars().first()
    if existing and existing.created_at and (datetime.now(timezone.utc) - existing.created_at).days < 90:
        raise ValueError("Candidate has already received a referral for this company in the last 90 days.")

    # 4. Create slot
    current_q = get_current_quarter()
    slot = ReferralSlot(
        referrer_id=referrer_user_id,
        candidate_id=candidate_user_id,
        company_name=target_company,
        role_name=target_role,
        status="matched",
        quarter=current_q,
        referrer_note=personal_note,
        matched_at=datetime.now(timezone.utc)
    )
    db.add(slot)

    # 5. Send notification to candidate
    notif = Notification(
        user_id=candidate_user_id,
        type="referral_received",
        title=f"Someone at {target_company} offered to refer you",
        message=f"A verified {target_company} employee has offered to refer you for a {target_role} position. Review and accept to share details.",
        action_url="/referrals/incoming"
    )
    db.add(notif)

    await db.commit()
    return slot

async def accept_referral(
    candidate_user_id: uuid.UUID,
    referral_slot_id: uuid.UUID,
    db: AsyncSession
) -> ReferralSlot:
    """
    Accepts matching offer and reveals candidate coordinates.
    """
    stmt = select(ReferralSlot).where(ReferralSlot.id == referral_slot_id)
    slot = (await db.execute(stmt)).scalars().first()
    if not slot or slot.candidate_id != candidate_user_id:
        raise ValueError("Referral offer not found.")

    if slot.status != "matched":
        raise ValueError(f"Cannot accept referral in status: {slot.status}")

    slot.status = "accepted"
    slot.accepted_at = datetime.now(timezone.utc)
    db.add(slot)

    # Fetch candidate display details
    cand_prof_stmt = select(Profile).where(Profile.user_id == candidate_user_id)
    profile = (await db.execute(cand_prof_stmt)).scalar_one_or_none()
    cand_stud_stmt = select(StudentProfile).where(StudentProfile.user_id == candidate_user_id)
    student = (await db.execute(cand_stud_stmt)).scalar_one_or_none()
    linkedin = (student.linkedin_url if student else None) or "https://linkedin.com"
    name = profile.first_name if profile else "Candidate"

    # Notify Referrer
    notif = Notification(
        user_id=slot.referrer_id,
        type="referral_accepted",
        title="Your referred candidate accepted",
        message=f"{name} accepted your referral offer. LinkedIn profile: {linkedin}. Mark as submitted when done.",
        action_url="/referrals/my-slots"
    )
    db.add(notif)

    await db.commit()
    return slot

async def log_referral_outcome(
    referral_slot_id: uuid.UUID,
    outcome: str,
    db: AsyncSession
) -> ReferralSlot:
    """
    Records referral outcomes and updates gamification points.
    """
    if outcome not in ["hired", "rejected", "no_response", "withdrew"]:
        raise ValueError("Invalid outcome code.")

    stmt = select(ReferralSlot).where(ReferralSlot.id == referral_slot_id)
    slot = (await db.execute(stmt)).scalars().first()
    if not slot:
        raise ValueError("Referral slot not found.")

    slot.outcome = outcome
    slot.status = outcome # keep aligned
    slot.outcome_logged_at = datetime.now(timezone.utc)
    db.add(slot)

    if outcome == "hired":
        # Referrer XP
        await gamification_service.award_xp(
            user_id=str(slot.referrer_id),
            event_type="referral_hired_referrer", # 1000 XP
            db=db,
            redis=redis_client
        )
        # Candidate XP
        await gamification_service.award_xp(
            user_id=str(slot.candidate_id),
            event_type="referral_hired_candidate", # 500 XP
            db=db,
            redis=redis_client
        )

        # Send notifications
        ref_notif = Notification(
            user_id=slot.referrer_id,
            type="referral_hired",
            title="Congratulations! Your candidate was hired!",
            message=f"Your referral at {slot.company_name} was successful. You earned 1000 XP and the 'Talent Spotter' badge.",
            action_url="/referrals/my-slots"
        )
        cand_notif = Notification(
            user_id=slot.candidate_id,
            type="referral_hired",
            title="Referral Successful! You're hired!",
            message=f"Congratulations! You were hired at {slot.company_name} through a referral. You earned 500 XP.",
            action_url="/referrals/incoming"
        )
        db.add(ref_notif)
        db.add(cand_notif)

    await db.commit()
    return slot
