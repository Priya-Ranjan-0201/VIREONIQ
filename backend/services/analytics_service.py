from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from db.models import (
    Application,
    CognitiveProfile,
    InterviewScore,
    InterviewSession,
    Profile,
    Resume,
    ResumeScore,
)
from typing import Dict, Any
import uuid
from services.intelligence.gap_analysis import GapAnalysisEngine
from services.intelligence.career_gps import CareerGPSNavigator
from services.intelligence.market_sync import MarketSyncEngine
from services.intelligence.dna_profiler import PsychometricDNAProfiler

# Initialize Engines
gap_engine = GapAnalysisEngine()
gps_navigator = CareerGPSNavigator()
market_sync = MarketSyncEngine()
dna_profiler = PsychometricDNAProfiler()

async def get_user_dashboard_stats(db: AsyncSession, user_id: uuid.UUID) -> Dict[str, Any]:
    # 1. Latest Resume & Profile
    profile_stmt = select(Profile).where(Profile.user_id == user_id)
    profile = (await db.execute(profile_stmt)).scalar_one_or_none()
    target_role = profile.target_role if profile else "Senior Backend Engineer"

    # Query real latest ATS resume score instead of returning a hardcoded constant
    ats_stmt = (
        select(ResumeScore.overall_score)
        .join(Resume, Resume.id == ResumeScore.resume_id)
        .where(Resume.user_id == user_id)
        .order_by(desc(ResumeScore.created_at))
        .limit(1)
    )
    latest_ats = (await db.execute(ats_stmt)).scalar_one_or_none()
    ats_score = round(float(latest_ats), 1) if latest_ats is not None else 0.0

    # Query real application tracker counts
    app_stmt = select(Application.status).where(Application.user_id == user_id)
    app_statuses = list((await db.execute(app_stmt)).scalars().all())
    app_total = len(app_statuses)
    app_offers = sum(1 for st in app_statuses if (st or "").lower() == "offer")
    app_active = sum(
        1 for st in app_statuses
        if (st or "").lower() not in {"rejected", "withdrawn", "offer"}
    )

    # 2. Latest Gap Analysis & Interview History
    interview_stmt = select(InterviewScore).join(InterviewSession).where(InterviewSession.user_id == user_id).order_by(desc(InterviewSession.started_at))
    interview_rows = (await db.execute(interview_stmt)).scalars().all()
    
    interview_history = []
    for row in interview_rows:
        interview_history.append({
            "tech_score": float(row.technical_correctness),
            "comm_score": float(row.communication_clarity),
            "scenario_score": float(row.technical_correctness),
            "depth_score": float(row.technical_correctness),
            "telemetry": {"avg_latency": 450}
        })
    
    intelligence_profile = gap_engine.calculate_current_profile(interview_history)
    # Scale for 5D
    profile_pct = {k: v * 100 for k, v in intelligence_profile.items()}
    
    # 3. Career GPS Rerouting
    gps_result = gps_navigator.calculate_reroute(intelligence_profile, target_role)
    milestones = gps_navigator.generate_milestones(target_role, intelligence_profile)
    
    # 4. Market Synchronicity
    market_opportunities = market_sync.get_market_opportunities(intelligence_profile)
    
    # 5. DNA & Archetype (read stored CognitiveProfile when available)
    cog_stmt = select(CognitiveProfile).where(CognitiveProfile.user_id == user_id)
    cog_profile = (await db.execute(cog_stmt)).scalar_one_or_none()
    if cog_profile and cog_profile.dominant_archetype:
        archetype = cog_profile.dominant_archetype
    elif cog_profile and cog_profile.dna_vector:
        archetype = dna_profiler.identify_archetype(cog_profile.dna_vector)
    else:
        archetype = "Unassessed"
    
    return {
        "ats_score": ats_score,
        "skill_match": profile_pct.get("Skill", 0),
        "intelligence_profile": profile_pct,
        "gps_reroute": gps_result,
        "milestones": milestones,
        "market_opportunities": market_opportunities,
        "dna_archetype": archetype,
        "interview_readiness": {
            "technical": profile_pct.get("Skill", 0),
            "communication": profile_pct.get("Communication", 0),
            "confidence": profile_pct.get("Confidence", 0),
        },
        "applications": {"total": app_total, "active": app_active, "offers": app_offers},
        "top_gaps": [g["dimension"] for g in gap_engine.identify_critical_gaps(intelligence_profile)][:3],
        "ai_therapist_insight": {
            "title": f"GPS Reroute: {gps_result['status']}",
            "message": f"Your current trajectory is {gps_result['status']}. {gps_result.get('reason', '')} Next Step: {gps_result['next_best_action']}",
            "proof": f"Market Alignment is {market_opportunities[0]['probability']}% for top-tier roles." if market_opportunities else "Scoring updated."
        },
        "culture_fit": {
            "google": market_sync.calculate_hiring_probability(intelligence_profile, "Google")["probability"],
            "amazon": market_sync.calculate_hiring_probability(intelligence_profile, "Amazon")["probability"],
            "meta": market_sync.calculate_hiring_probability(intelligence_profile, "Meta")["probability"],
            "dominant_trait": archetype
        }
    }

async def calculate_career_gps_navigation(
    db: AsyncSession,
    user_id: uuid.UUID,
    target_role: str = "Senior Backend Engineer",
    experience_years: str = "1-3 years",
    target_tier: str = "Tier-1 MNCs (Google, Amazon, Stripe)",
    time_horizon_days: int = 60,
    strategy: str = "FASTEST_PATH"
) -> Dict[str, Any]:
    # 1. Fetch user profile
    profile_stmt = select(Profile).where(Profile.user_id == user_id)
    profile = (await db.execute(profile_stmt)).scalar_one_or_none()
    effective_target_role = target_role or (profile.target_role if profile and profile.target_role else "Senior Backend Engineer")
    
    # 2. Latest Gap Analysis & Interview History
    interview_stmt = select(InterviewScore).join(InterviewSession).where(InterviewSession.user_id == user_id).order_by(desc(InterviewSession.started_at))
    interview_rows = (await db.execute(interview_stmt)).scalars().all()
    
    interview_history = []
    for row in interview_rows:
        interview_history.append({
            "tech_score": float(row.technical_correctness),
            "comm_score": float(row.communication_clarity),
            "scenario_score": float(row.technical_correctness),
            "depth_score": float(row.technical_correctness),
            "telemetry": {"avg_latency": 450}
        })
    
    intelligence_profile = gap_engine.calculate_current_profile(interview_history)
    
    return gps_navigator.calculate_full_navigation(
        profile=intelligence_profile,
        target_role=effective_target_role,
        experience_years=experience_years,
        target_tier=target_tier,
        time_horizon_days=time_horizon_days,
        strategy=strategy
    )




