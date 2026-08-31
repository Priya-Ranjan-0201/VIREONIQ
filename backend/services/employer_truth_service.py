import re
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from db.models import User, RealInterviewDebrief, EmployerTruthScore, EmployerFlag, Notification
from services.bias_detection_service import compute_company_bias_score

ETS_DIMENSIONS = {
    "process_transparency": {"weight": 0.20},
    "timeline_honesty": {"weight": 0.20},
    "ghost_rate": {"weight": 0.25},
    "feedback_quality": {"weight": 0.15},
    "equity_score": {"weight": 0.20}
}

SCORE_LABELS = {
    "Candidate First": {"min": 90, "max": 100, "color": "#10B981", "description": "Transparent, timely, respectful process"},
    "Fair Process": {"min": 75, "max": 89, "color": "#3B82F6", "description": "Generally respectful with minor gaps"},
    "Mixed Experience": {"min": 60, "max": 74, "color": "#F59E0B", "description": "Inconsistent candidate experience reported"},
    "Watch List": {"min": 40, "max": 59, "color": "#EF4444", "description": "Significant concerns reported across dimensions"},
    "Flagged": {"min": 0, "max": 39, "color": "#7F1D1D", "description": "Serious and consistent candidate experience failures"}
}

def get_label_for_score(score: float) -> Dict[str, Any]:
    for label, details in SCORE_LABELS.items():
        if details["min"] <= score <= details["max"]:
            return {"label": label, "color": details["color"], "description": details["description"]}
    return {"label": "Watch List", "color": "#EF4444", "description": "Significant concerns reported"}

async def compute_employer_truth_score(
    company_name: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Analyzes debrief profiles and computes the Employer Truth Score.
    """
    stmt = select(RealInterviewDebrief).where(RealInterviewDebrief.company_name.ilike(f"%{company_name}%"))
    submissions = (await db.execute(stmt)).scalars().all()
    total = len(submissions)

    if total < 10:
        return {
            "status": "insufficient_data",
            "submission_count": total,
            "needed": 10 - total
        }

    # 1. Process Transparency Score
    surprise_rounds = 0
    standard_rounds = ["hr_screening", "technical_round_1", "technical_round_2", "system_design", "managerial"]
    for s in submissions:
        if s.round_type and s.round_type not in standard_rounds:
            surprise_rounds += 1
            
    transparency_score = max(40.0, 100.0 - (surprise_rounds / total * 100.0))

    # 2. Timeline Honesty Score
    # Extract stated vs actual timelines via simple heuristics or LLM
    mismatches = 0
    for s in submissions:
        text = f"{s.what_worked or ''} {s.what_did_not_work or ''}"
        # Heuristic check for delays
        if any(word in text.lower() for word in ["delayed", "slow", "weeks to respond", "took too long", "late"]):
            mismatches += 1
            
    timeline_score = max(30.0, 100.0 - (mismatches / total * 100.0))

    # 3. Ghost Rate Score
    now_time = datetime.now(timezone.utc)
    ghost_count = sum(1 for s in submissions if s.outcome == "pending" and s.interview_date and (now_time - s.interview_date).days > 30)
    ghost_rate = (ghost_count / total) * 100.0
    ghost_score = max(0.0, 100.0 - (ghost_rate * 2.5))

    # 4. Feedback Quality Score
    rejected = [s for s in submissions if s.outcome == "failed"]
    specific_count = 0
    generic_count = 0
    
    for r in rejected:
        txt = (r.what_did_not_work or "").lower()
        if len(txt) > 80 or any(w in txt for w in ["recommend", "focus on", "weak in", "practise"]):
            specific_count += 1
        elif any(w in txt for w in ["generic", "templated", "no details", "sorry"]):
            generic_count += 1
            
    feedback_score = (specific_count * 100.0 + generic_count * 50.0) / max(len(rejected), 1)
    if not rejected:
        feedback_score = 80.0 # Default if no failures logged

    # 5. Equity Score (Session 25)
    eq_data = await compute_company_bias_score(company_name, db)
    equity_score = float(eq_data["equity_score"])

    # Final Weighted ETS
    weighted_ets = (
        (transparency_score * ETS_DIMENSIONS["process_transparency"]["weight"]) +
        (timeline_score * ETS_DIMENSIONS["timeline_honesty"]["weight"]) +
        (ghost_score * ETS_DIMENSIONS["ghost_rate"]["weight"]) +
        (feedback_score * ETS_DIMENSIONS["feedback_quality"]["weight"]) +
        (equity_score * ETS_DIMENSIONS["equity_score"]["weight"])
    )

    label_details = get_iso_label = get_label_for_score(weighted_ets)
    
    # Save/Update in db
    exist_stmt = select(EmployerTruthScore).where(EmployerTruthScore.company_name == company_name)
    ets = (await db.execute(exist_stmt)).scalars().first()
    
    if not ets:
        ets = EmployerTruthScore(company_name=company_name)
        db.add(ets)
        
    ets.overall_score = Decimal(str(weighted_ets))
    ets.label = label_details["label"]
    ets.transparency_score = Decimal(str(transparency_score))
    ets.timeline_score = Decimal(str(timeline_score))
    ets.ghost_rate = Decimal(str(ghost_rate))
    ets.feedback_score = Decimal(str(feedback_score))
    ets.equity_score = Decimal(str(equity_score))
    ets.submission_count = total
    ets.last_computed_at = datetime.now(timezone.utc)

    await db.commit()
    return ets

async def flag_company_for_review(
    company_name: str,
    reason: str,
    reported_by: uuid.UUID,
    db: AsyncSession
) -> None:
    """
    Creates a flag alert and moves low-scoring employers to review.
    """
    flag = EmployerFlag(
        company_name=company_name,
        reason=reason,
        reported_by_user_id=reported_by,
        status="pending"
    )
    db.add(flag)

    # Check score
    stmt = select(EmployerTruthScore).where(EmployerTruthScore.company_name == company_name)
    ets = (await db.execute(stmt)).scalars().first()
    if ets and ets.overall_score and ets.overall_score < 40:
        ets.label = "Flagged"
        db.add(ets)
        
        # Notify admins
        # Fetch an admin user id
        admin_stmt = select(User).where(User.role == "admin").limit(1)
        admin = (await db.execute(admin_stmt)).scalars().first()
        if admin:
            notif = Notification(
                user_id=admin.id,
                type="SYSTEM",
                title=f"Flagged Employer Alert: {company_name}",
                message=f"Employer '{company_name}' has been flagged. Score: {ets.overall_score}. Reason: {reason}",
                action_url="/admin"
            )
            db.add(notif)

    await db.commit()

async def get_ets_leaderboard(
    category: str,
    db: AsyncSession
) -> List[Dict[str, Any]]:
    """
    Queries employer truth scores by filter categories.
    """
    stmt = select(EmployerTruthScore).where(EmployerTruthScore.submission_count >= 10)
    
    if category == "best":
        stmt = stmt.order_by(EmployerTruthScore.overall_score.desc())
    elif category == "worst":
        stmt = stmt.order_by(EmployerTruthScore.overall_score.asc())
    elif category == "most_improved":
        # Sort by difference if prev_month_score exists
        stmt = stmt.order_by((EmployerTruthScore.overall_score - EmployerTruthScore.prev_month_score).desc())
    else:
        stmt = stmt.order_by(EmployerTruthScore.overall_score.desc())

    stmt = stmt.limit(20)
    records = (await db.execute(stmt)).scalars().all()
    
    leaderboard = []
    for r in records:
        leaderboard.append({
            "company_name": r.company_name,
            "overall_score": float(r.overall_score) if r.overall_score else 0.0,
            "label": r.label,
            "ghost_rate": float(r.ghost_rate) if r.ghost_rate else 0.0,
            "submission_count": r.submission_count,
            "transparency_score": float(r.transparency_score) if r.transparency_score else 0.0,
            "timeline_score": float(r.timeline_score) if r.timeline_score else 0.0,
            "feedback_score": float(r.feedback_score) if r.feedback_score else 0.0,
            "equity_score": float(r.equity_score) if r.equity_score else 0.0
        })
    return leaderboard
