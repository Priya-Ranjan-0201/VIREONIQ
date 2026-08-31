"""
Offer Letter generation service.
Computes placement readiness score (PRS), evaluates interview stage outcomes, and generates mock offer/rejection/development letters via LLM.
"""

import uuid
import logging
import random
from datetime import datetime, timezone, date, timedelta
from typing import Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import OfferLetter, InterviewSession, InterviewScore, Profile, GapAnalysis, StudentProfile
from core.llm.nvidia import NVIDIA_NIM_Client  # Use standard core LLM helpers or fallback to Anthropic if set up
from core.config import settings

logger = logging.getLogger(__name__)

STAGE_WEIGHTS = {
    "technical_round_1": 0.15,
    "technical_round_2": 0.20,
    "hr": 0.15,
    "aptitude": 0.10,
    "communication": 0.15,
    "project_defense": 0.12,
    "code": 0.10,
    "gap_closure": 0.03
}

COMPANY_CTC_MAP = {
    "backend_developer_product": (18, 35),
    "backend_developer_faang": (30, 60),
    "backend_developer_startup": (12, 25),
    "backend_developer_service": (6, 12),
    "software_developer_service": (6, 12),
    "software_developer_product": (12, 25),
    "data_analyst_product": (15, 28),
    "ai_ml_engineer_product": (25, 50),
    "ai_ml_engineer_faang": (40, 80)
}

async def generate_offer_letter(user_id: str, db: AsyncSession, anthropic_client = None) -> Dict[str, Any]:
    """
    Computes cumulative Placement Readiness Score (PRS) and requests LLM to generate
    an offer, rejection, or development letter.
    """
    logger.info(f"Generating offer letter for user_id={user_id}")
    
    # 1. Fetch completed sessions
    uid = uuid.UUID(user_id)
    sess_stmt = select(InterviewSession).where(InterviewSession.user_id == uid, InterviewSession.status == "completed")
    sessions = (await db.execute(sess_stmt)).scalars().all()
    
    session_scores = []
    weighted_sum = 0.0
    weight_total = 0.0

    for s in sessions:
        score_stmt = select(InterviewScore).where(InterviewScore.session_id == s.id)
        score_row = (await db.execute(score_stmt)).scalar_one_or_none()
        
        if score_row:
            # overall score between 0 and 100
            tech = float(score_row.technical_correctness or 5.0) * 10.0
            comm = float(score_row.communication_clarity or 5.0) * 10.0
            conf = float(score_row.confidence_tone or 5.0) * 10.0
            comp = float(score_row.completeness or 5.0) * 10.0
            avg_score = (tech + comm + conf + comp) / 4.0
            
            mode = s.session_mode or "technical_round_1"
            w = STAGE_WEIGHTS.get(mode, 0.05)
            weighted_sum += avg_score * w
            weight_total += w
            
            session_scores.append({
                "stage": mode,
                "score": avg_score,
                "feedback": score_row.feedback_summary
            })

    prs = 60.0 # Default if no scores
    if weight_total > 0:
        prs = min(100.0, weighted_sum / weight_total)

    # 2. Fetch profile data
    prof_stmt = select(Profile).where(Profile.user_id == uid)
    profile = (await db.execute(prof_stmt)).scalar_one_or_none()
    
    role = profile.target_role if profile and profile.target_role else "backend_developer"
    company_type = profile.target_company_type if profile and profile.target_company_type else "product"
    
    # Format key for CTC lookup
    ctc_key = f"{role.lower().replace(' ', '_')}_{company_type.lower()}"
    ctc_range = COMPANY_CTC_MAP.get(ctc_key, (10, 20))
    ctc_val = round(random.uniform(ctc_range[0], ctc_range[1]), 2)

    # 3. Determine letter type
    if prs >= 75.0:
        letter_type = "offer"
    elif prs >= 50.0:
        letter_type = "rejection"
    else:
        letter_type = "development"

    # Fetch latest gaps
    gap_stmt = select(GapAnalysis).where(GapAnalysis.user_id == uid).order_by(GapAnalysis.created_at.desc())
    gap_analysis = (await db.execute(gap_stmt)).scalars().first()
    gaps_str = ", ".join(gap_analysis.missing_skills) if gap_analysis and gap_analysis.missing_skills else "system components"

    # Formulate joining date and location
    joining_date = (date.today() + timedelta(days=30)).isoformat()
    location = random.choice(["Bengaluru", "Hyderabad", "Pune", "Mumbai", "Delhi NCR"])
    company_name = random.choice(["Google", "Microsoft", "Stripe", "Flipkart", "Infosys", "Razorpay", "Cred"])

    # Setup prompt
    scores_summary = "\n".join(f"- {s['stage']}: {s['score']:.1f}/100 ({s['feedback'][:100]}...)" for s in session_scores)

    if letter_type == "offer":
        prompt = f"""
        Generate a mock job offer letter for a {role} position at a {company_type} company named {company_name} in India.
        The candidate scored {prs:.1f}/100 in their placement simulation.
        Include:
        - Congratulations opening referencing specific strengths from these session scores:
        {scores_summary}
        - Role: {role}
        - Company: {company_name}
        - CTC: {ctc_val} LPA (lakhs per annum)
        - Location: {location}
        - Joining date: {joining_date}
        - 3 specific strengths that led to selection, derived from actual scores.
        
        Return ONLY valid JSON format with keys:
        "greeting": "...",
        "strengths_paragraph": "...",
        "offer_details": "...",
        "next_steps": "...",
        "closing": "..."
        """
    elif letter_type == "rejection":
        prompt = f"""
        Generate a professional, warm, but clear rejection letter for a {role} position at {company_name}.
        The candidate scored {prs:.1f}/100 overall.
        Analyze scores:
        {scores_summary}
        State the exact stage that performed below threshold (with actual score), and give a specific re-evaluation/improvement timeline of 6 months.
        Return ONLY valid JSON format with keys:
        "greeting": "...",
        "feedback_paragraph": "...",
        "decision_details": "...",
        "improvement_timeline": "...",
        "closing": "..."
        """
    else:
        prompt = f"""
        Generate a development-focused mock letter advising further preparation for a {role} position.
        The candidate scored {prs:.1f}/100.
        Gaps: {gaps_str}
        Detail specific areas for improvement before re-attempting a mock placement.
        Return ONLY valid JSON format with keys:
        "greeting": "...",
        "assessment": "...",
        "critical_gaps": "...",
        "action_plan": "...",
        "closing": "..."
        """

    # Generate via LLM (NVIDIA NIM or Anthropic fallback)
    letter_json = {}
    try:
        if settings.ANTHROPIC_API_KEY:
            # import client dynamically
            from anthropic import Anthropic
            client = anthropic_client or Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            resp = client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            raw_content = resp.content[0].text
        else:
            client = NVIDIA_NIM_Client()
            raw_content = await client.generate(prompt)

        # Parse JSON from LLM output
        import json
        import re
        match = re.search(r"\{.*\}", raw_content, re.DOTALL)
        if match:
            letter_json = json.loads(match.group(0))
        else:
            letter_json = {"greeting": "Hello,", "letter_body": raw_content, "closing": "Best regards"}
    except Exception as e:
        logger.error(f"Failed to generate offer letter via LLM: {e}")
        # fallback simple JSON
        letter_json = {
            "greeting": "Dear Candidate,",
            "offer_details": f"Offer for {role} at {company_name}. CTC: {ctc_val} LPA. Location: {location}.",
            "strengths_paragraph": "We were impressed with your technical precision and interview composure.",
            "next_steps": "Please accept this offer via dashboard link.",
            "closing": "Warm regards, Recruitment Team"
        }

    # Save to PostgreSQL
    offer_letter_row = OfferLetter(
        user_id=uid,
        letter_type=letter_type,
        readiness_score_at_generation=prs,
        simulated_company=company_name,
        simulated_role=role,
        ctc_offered_thousands=int(ctc_val * 100),
        letter_content=letter_json
    )
    
    db.add(offer_letter_row)
    await db.commit()
    await db.refresh(offer_letter_row)
    
    return {
        "id": str(offer_letter_row.id),
        "letter_type": letter_type,
        "simulated_company": company_name,
        "simulated_role": role,
        "readiness_score": prs,
        "ctc": ctc_val,
        "content": letter_json
    }
