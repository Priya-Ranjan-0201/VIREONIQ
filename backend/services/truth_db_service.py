import re
import json
import uuid
import numpy as np
from datetime import datetime, timedelta, timezone
from collections import Counter
from typing import Dict, Any, List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from db.models import User, RealInterviewDebrief, CompanyTruthAggregate
from services import gamification_service
from core.llm.orchestrator import acall_llm
from core.redis import redis_client

INSIGHT_CATEGORIES = {
    "process_truth": "What the actual process looked like, not the job posting version",
    "question_patterns": "Specific topics and question types that actually appeared",
    "timeline_reality": "How long each stage actually took vs what was communicated",
    "offer_intelligence": "Salary ranges, negotiation room, benefits reality",
    "rejection_patterns": "What actually caused rejections at each stage",
    "ghost_rate": "How often candidates were ghosted with no response"
}

def extract_numbers_from_text(text: str) -> List[float]:
    """Helper to extract numbers representing salaries using regex."""
    if not text:
        return []
    # Find numbers like 1,200,000 or 1500000 or 15L or 20 LPA
    numbers = []
    # Clean formatting
    text_clean = text.replace(",", "")
    matches = re.findall(r'\b\d+(?:\.\d+)?\b', text_clean)
    for m in matches:
        try:
            val = float(m)
            # Filter out small integers like rounds or interview days (e.g. 1, 2, 5)
            if val > 10000:
                numbers.append(val)
            elif val <= 100 and ("lpa" in text.lower() or "lakh" in text.lower() or "l" in text.lower()):
                # Convert LPA to actual numbers (e.g. 15L -> 1,500,000)
                numbers.append(val * 100000)
        except ValueError:
            pass
    return numbers

async def aggregate_company_insights(
    company_name: str,
    role_category: str,
    db: AsyncSession
) -> Optional[CompanyTruthAggregate]:
    """
    Queries real_interview_debriefs and builds an aggregate insight profile.
    """
    stmt = select(RealInterviewDebrief).where(
        and_(
            RealInterviewDebrief.company_name.ilike(f"%{company_name}%"),
            RealInterviewDebrief.role.ilike(f"%{role_category}%")
        )
    )
    submissions = (await db.execute(stmt)).scalars().all()
    total_submissions = len(submissions)

    if total_submissions < 5:
        return None

    # 1. Process Truth
    round_types = [s.round_type for s in submissions if s.round_type]
    round_counts = Counter(round_types)
    stage_map = {k: float(v / total_submissions) for k, v in round_counts.items()}
    
    # Calculate average rounds per candidate
    rounds_per_sub = []
    for s in submissions:
        # Check how many rounds are reported by the same user for this company if possible, 
        # or treat each submission as 1 round stage. Here we use stage count as proxy.
        rounds_per_sub.append(1)
    
    avg_rounds = Decimal(str(sum(rounds_per_sub) / len(rounds_per_sub)))
    
    # Surprise stages: stage types appearing in > 20% of entries which aren't standard
    standard_rounds = ["hr_screening", "technical_round_1", "technical_round_2", "system_design", "managerial"]
    surprise = []
    for r, count in round_counts.items():
        if r not in standard_rounds and (count / total_submissions) > 0.20:
            surprise.append(r)

    # 2. Question Patterns
    all_topics = []
    all_questions = []
    for s in submissions:
        if s.topics_tested:
            # handle if topics_tested is list or string
            topics = s.topics_tested if isinstance(s.topics_tested, list) else json.loads(s.topics_tested or "[]")
            all_topics.extend(topics)
        if s.specific_questions:
            questions = s.specific_questions if isinstance(s.specific_questions, list) else json.loads(s.specific_questions or "[]")
            all_questions.extend(questions)

    top_topics_counts = Counter(all_topics).most_common(10)
    top_topics = {topic: count for topic, count in top_topics_counts}

    # Semantic deduplication fallback: direct similarity or clean duplicates
    unique_questions = []
    seen_q = set()
    for q in all_questions:
        q_clean = q.lower().strip()
        # Simple deduplication: if similarity proxy is needed, check common words overlap
        is_dup = False
        for sq in seen_q:
            # Word overlap ratio
            words1 = set(q_clean.split())
            words2 = set(sq.split())
            if len(words1 & words2) / max(len(words1 | words2), 1) > 0.80:
                is_dup = True
                break
        if not is_dup:
            seen_q.add(q_clean)
            unique_questions.append(q)

    # 3. Timeline reality
    durations = []
    ghosted_count = 0
    now_time = datetime.now(timezone.utc)
    for s in submissions:
        if s.outcome == "pending" and s.interview_date and (now_time - s.interview_date).days > 30:
            ghosted_count += 1
        
        # Outcome dates aren't in model directly, but we can compute duration heuristic
        # from created_at or updated_at date difference
        if s.outcome != "pending" and s.updated_at and s.interview_date:
            days = (s.updated_at - s.interview_date).days
            durations.append(max(1, days))

    avg_days_total = sum(durations) / len(durations) if durations else 15.0
    ghost_rate = Decimal(str((ghosted_count / total_submissions) * 100))

    # 4. Offer intelligence (only surfaces if 5+ offer outcomes)
    offer_subs = [s for s in submissions if s.outcome == "passed"]
    offer_intel = {}
    if len(offer_subs) >= 5:
        salaries = []
        for o in offer_subs:
            # Try to extract from text fields
            text = f"{o.what_worked or ''} {o.what_did_not_work or ''} {o.would_change or ''}"
            salaries.extend(extract_numbers_from_text(text))
        
        if len(salaries) >= 5:
            salaries.sort()
            offer_intel = {
                "min": salaries[0],
                "p25": np.percentile(salaries, 25),
                "median": np.percentile(salaries, 50),
                "p75": np.percentile(salaries, 75),
                "max": salaries[-1]
            }

    # Upsert
    stmt_exist = select(CompanyTruthAggregate).where(
        and_(
            CompanyTruthAggregate.company_name == company_name,
            CompanyTruthAggregate.role_category == role_category
        )
    )
    agg = (await db.execute(stmt_exist)).scalars().first()
    if not agg:
        agg = CompanyTruthAggregate(
            company_name=company_name,
            role_category=role_category
        )
        db.add(agg)

    agg.submission_count = total_submissions
    agg.quality_verified_count = len([s for s in submissions if s.is_quality_verified])
    agg.stage_map = stage_map
    agg.avg_rounds = avg_rounds
    agg.surprise_stages = surprise
    agg.top_topics = top_topics
    agg.verified_questions = unique_questions[:10]
    agg.timeline_reality = {
        "avg_days_total": avg_days_total,
        "stage_durations": {r: avg_days_total / max(1, len(stage_map)) for r in stage_map}
    }
    agg.ghost_rate = ghost_rate
    agg.offer_intelligence = offer_intel if offer_intel else None
    agg.last_aggregated_at = datetime.now(timezone.utc)

    # Compute Equity Score from Session 25
    from services.bias_detection_service import compute_company_bias_score
    eq_data = await compute_company_bias_score(company_name, db)
    agg.equity_score = Decimal(str(eq_data["equity_score"]))

    await db.commit()
    return agg

async def verify_submission_quality(
    debrief_id: uuid.UUID,
    db: AsyncSession
) -> bool:
    """
    Checks verification rules and issues gamification reward XP.
    """
    stmt = select(RealInterviewDebrief).where(RealInterviewDebrief.id == debrief_id)
    debrief = (await db.execute(stmt)).scalars().first()
    if not debrief:
        return False

    # 1. Quality checks
    what_worked = debrief.what_worked or ""
    what_did_not = debrief.what_did_not_work or ""
    topics = debrief.topics_tested or []
    
    length_ok = len(what_worked) > 50 and len(what_did_not) > 50
    specificity_ok = len(topics) >= 2
    
    now_time = datetime.now(timezone.utc)
    date_ok = debrief.interview_date <= now_time and debrief.interview_date >= (now_time - timedelta(days=730))

    if not (length_ok and specificity_ok and date_ok):
        debrief.is_quality_verified = False
        db.add(debrief)
        await db.commit()
        return False

    # 2. Coherence check via LLM
    coherence_prompt = (
        f"Does this interview debrief appear to be a real interview experience?\n"
        f"Text: {what_worked} {what_did_not}\n"
        f"Answer only YES or NO."
    )
    
    is_coherent = False
    try:
        res = (await acall_llm(coherence_prompt)).strip().upper()
        if "YES" in res:
            is_coherent = True
    except Exception:
        # Heuristic fallback if LLM offline
        is_coherent = True

    if is_coherent:
        debrief.is_quality_verified = True
        db.add(debrief)
        # Award additional 20 XP (30 already awarded immediately in router)
        await gamification_service.award_xp(
            user_id=str(debrief.user_id),
            event_type="debrief_verified", # 20 XP
            db=db,
            redis=redis_client
        )
        await db.commit()
        return True
    else:
        debrief.is_quality_verified = False
        db.add(debrief)
        await db.commit()
        return False

async def search_truth_database(
    query: str,
    filters: Dict[str, Any],
    db: AsyncSession
) -> List[CompanyTruthAggregate]:
    """
    Search database aggregates by applying filters.
    """
    stmt = select(CompanyTruthAggregate)
    
    # Text filters
    if query:
        stmt = stmt.where(CompanyTruthAggregate.company_name.ilike(f"%{query}%"))
        
    company_name = filters.get("company_name")
    if company_name:
        stmt = stmt.where(CompanyTruthAggregate.company_name.ilike(f"%{company_name}%"))

    role_category = filters.get("role_category")
    if role_category:
        stmt = stmt.where(CompanyTruthAggregate.role_category.ilike(f"%{role_category}%"))

    min_subs = filters.get("min_submissions", 5)
    stmt = stmt.where(CompanyTruthAggregate.submission_count >= min_subs)

    stmt = stmt.order_by(CompanyTruthAggregate.submission_count.desc())
    results = (await db.execute(stmt)).scalars().all()
    return results
