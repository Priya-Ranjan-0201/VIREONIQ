from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import User, InterviewScore, Offer
from core.llm.factory import get_llm_provider
from typing import Dict, Any
import uuid

OFFER_GENERATION_PROMPT = """
You are a Senior HR Director at a top-tier tech company.
Based on the candidate's interview performance and target role, generate a realistic mock offer package.

CANDIDATE INTERVIEW SCORES:
Technical: {tech_score}/100
Communication: {comm_score}/100
Confidence: {conf_score}/100

TARGET ROLE: {role}
MARKET BASE SALARY: {base_salary}

OUTPUT FORMAT:
Return ONLY a valid JSON object:
{{
  "base_salary": float,
  "currency": "INR",
  "joining_bonus": float,
  "equity_text": "string (e.g., 2000 RSU over 4 years)",
  "benefits": ["string"],
  "negotiation_leverage": "High" | "Medium" | "Low",
  "negotiation_tips": ["string"]
}}
"""

NEGOTIATION_COACHING_PROMPT = """
You are an elite career strategist and salary negotiation expert.
The candidate just received the following job offer. Provide a comprehensive negotiation strategy.

OFFER DETAILS:
Base Salary: {base_salary} INR
Joining Bonus: {joining_bonus} INR
Equity: {equity}
Negotiation Leverage: {leverage}

OUTPUT FORMAT:
Return ONLY a valid JSON object:
{{
  "opening_counter": {{
    "base_salary": float,
    "rationale": "string"
  }},
  "scripts": [
    {{
      "scenario": "string (e.g., 'When they say the salary is fixed')",
      "script": "string (exact words to say)"
    }}
  ],
  "red_lines": ["string (things never to say or do)"],
  "best_time_to_negotiate": "string",
  "confidence_score": float (0-100)
}}
"""

async def generate_mock_offer(db: AsyncSession, user_id: Any, session_id: str) -> Dict[str, Any]:
    """
    Fetch interview scores for the given session or use calibrated presets to generate
    a realistic mock offer package with negotiation leverage analysis.
    """
    PRESETS = {
        "google_sde": {
            "base_salary": 2400000,
            "currency": "INR",
            "joining_bonus": 400000,
            "equity_text": "₹14,00,000 GSU per year (4-year vesting with 33/33/22/12 split)",
            "benefits": ["Comprehensive Medical + OPD", "Free Gourmet Meals", "Annual Wellness Stipend", "Generous Parental Leave"],
            "negotiation_leverage": "High",
            "negotiation_tips": [
                "Google recruiters often have flexibility of +10-15% on Base if you present competing tier-1 product offers.",
                "Target an increase in Year-1 signing bonus if base salary hit the L3 band ceiling.",
                "Mention your verified distributed systems micro-internship credentials to justify upper-band placement."
            ]
        },
        "stripe_infra": {
            "base_salary": 2800000,
            "currency": "INR",
            "joining_bonus": 500000,
            "equity_text": "₹15,00,000 RSUs per year (Standard 1-year cliff, quarterly vesting)",
            "benefits": ["100% Remote Flexibility", "₹1,50,000 Home Office Grant", "Global Offsite Stipend", "Medical Insurance"],
            "negotiation_leverage": "High",
            "negotiation_tips": [
                "Stripe values extreme technical craftsmanship; highlight your reliability and idempotent architecture experience.",
                "Ask for an increase in signing bonus to offset any unvested stock left at your prior company."
            ]
        },
        "zepto_core": {
            "base_salary": 1800000,
            "currency": "INR",
            "joining_bonus": 250000,
            "equity_text": "₹6,00,000 ESOPs per year (4-year vesting schedule)",
            "benefits": ["Fast-Track Promotion Cycle", "Health Insurance", "Late Night Cab/Food Allowance"],
            "negotiation_leverage": "Medium",
            "negotiation_tips": [
                "High-growth startups are cash-conscious but equity-generous; request a 25% bump in ESOP allocation.",
                "Request a guaranteed 6-month performance appraisal milestone with predefined promotion metrics."
            ]
        }
    }

    sid_lower = str(session_id).lower()
    for key, preset in PRESETS.items():
        if key in sid_lower:
            return preset

    # Check if session_id is a valid UUID
    try:
        parsed_uuid = uuid.UUID(str(session_id))
        stmt = select(InterviewScore).where(InterviewScore.session_id == parsed_uuid)
        score = (await db.execute(stmt)).scalar_one_or_none()
        if score:
            llm = get_llm_provider()
            prompt = OFFER_GENERATION_PROMPT.format(
                tech_score=float(score.technical_correctness),
                comm_score=float(score.communication_clarity),
                conf_score=float(score.confidence_tone),
                role="Software Development Engineer",
                base_salary=2000000
            )
            offer_data = await llm.generate_json(
                messages=[{"role": "user", "content": "Generate the offer package."}],
                system_prompt=prompt
            )
            return offer_data
    except Exception:
        pass

    # Default calibrated Tier-1 offer
    return PRESETS["google_sde"]


async def get_negotiation_strategy(db: AsyncSession, offer_id: uuid.UUID) -> Dict[str, Any]:
    """
    Retrieve a stored offer record and generate a personalised AI negotiation
    coaching report with counter-offer scripts, red lines, and timing advice.
    """
    stmt = select(Offer).where(Offer.id == offer_id)
    offer = (await db.execute(stmt)).scalar_one_or_none()

    if not offer:
        return {"error": "Offer not found."}

    llm = get_llm_provider()
    prompt = NEGOTIATION_COACHING_PROMPT.format(
        base_salary=float(offer.base_salary) if offer.base_salary else 0,
        joining_bonus=float(offer.joining_bonus) if offer.joining_bonus else 0,
        equity=offer.equity_text or "Not specified",
        leverage=offer.negotiation_leverage or "Medium"
    )

    strategy = await llm.generate_json(
        messages=[{"role": "user", "content": "Give me a negotiation strategy for this offer."}],
        system_prompt=prompt
    )
    return strategy

