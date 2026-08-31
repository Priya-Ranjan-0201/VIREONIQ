import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import User, Profile, StudentProfile, SkillCredential, LanguageProgression, TalentPassport
from core.llm.orchestrator import acall_llm
from core.redis import redis_client

REMOTE_HIRING_TIERS = {
    "tier_1_global": {
        "description": "Hires from any country. No location preference. Async-first culture.",
        "examples": ["GitLab", "Automattic", "Basecamp", "Zapier", "Buffer"],
        "visa_requirement": "none",
        "salary_structure": "location_independent"
    },
    "tier_2_regional": {
        "description": "Hires from specific regions. Some timezone overlap required.",
        "examples": ["Many EU startups for APAC/EMEA", "US companies for LATAM"],
        "visa_requirement": "contractor_agreement",
        "salary_structure": "regional_adjusted"
    },
    "tier_3_visa_sponsor": {
        "description": "Willing to relocate and sponsor visa for exceptional candidates.",
        "examples": ["FAANG with global offices", "Large enterprise companies"],
        "visa_requirement": "work_visa",
        "salary_structure": "destination_country_rate"
    }
}

COUNTRY_HIRING_PROFILES = {
    "IN": {
        "name": "India",
        "strongest_export_roles": ["backend_developer", "data_engineer", "ML_engineer"],
        "companies_with_india_history": "large_set_from_market_data",
        "typical_contractor_rate_usd": {"junior": 20, "mid": 40, "senior": 70},
        "visa_pathways": ["H1B_lottery", "UK_global_talent", "Canada_express_entry", "Germany_job_seeker", "Netherlands_highly_skilled"],
        "remote_readiness_signals": ["github_activity_timezone_overlap", "english_credential_score"],
        "ppp_conversion_factor": 0.33
    },
    "NG": {
        "name": "Nigeria",
        "strongest_export_roles": ["backend_developer", "product_manager", "data_analyst"],
        "typical_contractor_rate_usd": {"junior": 15, "mid": 30, "senior": 55},
        "visa_pathways": ["UK_global_talent", "Canada_express_entry", "Germany_job_seeker"],
        "ppp_conversion_factor": 0.28
    },
    "ID": {
        "name": "Indonesia",
        "strongest_export_roles": ["mobile_developer", "data_analyst"],
        "typical_contractor_rate_usd": {"junior": 15, "mid": 30, "senior": 55},
        "visa_pathways": ["Germany_job_seeker", "Canada_express_entry"],
        "ppp_conversion_factor": 0.35
    },
    "BR": {
        "name": "Brazil",
        "strongest_export_roles": ["backend_developer", "UX_designer"],
        "typical_contractor_rate_usd": {"junior": 18, "mid": 35, "senior": 60},
        "visa_pathways": ["Portugal_d7", "Canada_express_entry"],
        "ppp_conversion_factor": 0.40
    },
    "PK": {
        "name": "Pakistan",
        "strongest_export_roles": ["backend_developer", "ML_engineer"],
        "typical_contractor_rate_usd": {"junior": 12, "mid": 25, "senior": 50},
        "visa_pathways": ["Canada_express_entry", "UK_global_talent"],
        "ppp_conversion_factor": 0.25
    },
    "BD": {
        "name": "Bangladesh",
        "strongest_export_roles": ["backend_developer", "frontend_developer"],
        "typical_contractor_rate_usd": {"junior": 10, "mid": 22, "senior": 45},
        "visa_pathways": ["Canada_express_entry"],
        "ppp_conversion_factor": 0.26
    },
    "EG": {
        "name": "Egypt",
        "strongest_export_roles": ["backend_developer", "cybersecurity"],
        "typical_contractor_rate_usd": {"junior": 12, "mid": 25, "senior": 50},
        "visa_pathways": ["Germany_job_seeker", "Canada_express_entry"],
        "ppp_conversion_factor": 0.29
    },
    "KE": {
        "name": "Kenya",
        "strongest_export_roles": ["data_analyst", "product_manager"],
        "typical_contractor_rate_usd": {"junior": 10, "mid": 22, "senior": 45},
        "visa_pathways": ["Canada_express_entry"],
        "ppp_conversion_factor": 0.30
    },
    "GH": {
        "name": "Ghana",
        "strongest_export_roles": ["mobile_developer", "backend_developer"],
        "typical_contractor_rate_usd": {"junior": 10, "mid": 22, "senior": 45},
        "visa_pathways": ["Canada_express_entry"],
        "ppp_conversion_factor": 0.31
    },
    "VN": {
        "name": "Vietnam",
        "strongest_export_roles": ["mobile_developer", "QA_engineer"],
        "typical_contractor_rate_usd": {"junior": 12, "mid": 25, "senior": 50},
        "visa_pathways": ["Japan_highly_skilled", "Canada_express_entry"],
        "ppp_conversion_factor": 0.34
    }
}

def bridge_phase_to_proficiency_label(phase: int) -> str:
    if phase <= 2:
        return "Native Language Speaker — Technical Skills Verified"
    elif phase <= 4:
        return "Bilingual — Building Professional English"
    return "Professional English — Full Interview Ready"

async def generate_talent_passport(
    user_id: uuid.UUID,
    db: AsyncSession
) -> TalentPassport:
    """
    Synthesizes credentials, profiles, and progression metrics into a global talent passport.
    """
    # 1. Fetch related rows
    prof_stmt = select(Profile).where(Profile.user_id == user_id)
    profile = (await db.execute(prof_stmt)).scalar_one_or_none()
    
    stud_stmt = select(StudentProfile).where(StudentProfile.user_id == user_id)
    student = (await db.execute(stud_stmt)).scalar_one_or_none()
    
    cred_stmt = select(SkillCredential).where(SkillCredential.user_id == user_id)
    credential = (await db.execute(cred_stmt)).scalars().first()
    
    prog_stmt = select(LanguageProgression).where(LanguageProgression.user_id == user_id)
    prog = (await db.execute(prog_stmt)).scalars().first()

    # Detect country
    # Standard location lookup, default to 'IN' if unspecified
    country = "IN"
    if student and student.city:
        # Check if country matches common codes
        for code, details in COUNTRY_HIRING_PROFILES.items():
            if details["name"].lower() in student.city.lower() or code.lower() in student.city.lower():
                country = code
                break

    country_profile = COUNTRY_HIRING_PROFILES.get(country, COUNTRY_HIRING_PROFILES["IN"])

    # Base values
    prs = float(profile.placement_readiness_score) if profile and profile.placement_readiness_score else 65.0
    tier = credential.tier if credential else "silver"
    completed_sessions = credential.sessions_completed if credential else 5
    bridge_phase = prog.current_bridge_phase if prog else 3
    
    passport_id = f"PLACEIQ-{str(user_id)[:8].upper()}-{datetime.now().year}"

    # Classify eligible remote tiers
    eligible_tiers = []
    if prs >= 88:
        eligible_tiers = ["tier_1_global", "tier_2_regional", "tier_3_visa_sponsor"]
    elif prs >= 70:
        eligible_tiers = ["tier_2_regional"]
    else:
        eligible_tiers = ["tier_3_visa_sponsor"]

    # Salary rates
    min_rate = country_profile["typical_contractor_rate_usd"]["junior"]
    max_rate = country_profile["typical_contractor_rate_usd"]["senior"]
    if tier == "gold" or tier == "platinum":
        min_rate = country_profile["typical_contractor_rate_usd"]["mid"]
    elif tier == "diamond":
        min_rate = country_profile["typical_contractor_rate_usd"]["senior"]

    public_passport_url = f"https://placeiq.app/passport/{passport_id}"

    # Upsert TalentPassport table
    stmt = select(TalentPassport).where(TalentPassport.user_id == user_id)
    passport = (await db.execute(stmt)).scalars().first()
    if not passport:
        passport = TalentPassport(user_id=user_id)
        db.add(passport)

    passport.passport_id = passport_id
    passport.country_code = country
    passport.verified_role = profile.target_role if profile else "Software Developer"
    passport.skill_tier = tier
    passport.prs_score = Decimal(str(prs))
    passport.english_proficiency_tier = bridge_phase_to_proficiency_label(bridge_phase)
    passport.eligible_company_tiers = eligible_tiers
    passport.visa_pathways = country_profile["visa_pathways"]
    passport.contractor_rate_min = min_rate
    passport.contractor_rate_max = max_rate
    passport.public_passport_url = public_passport_url
    passport.last_updated_at = datetime.now(timezone.utc)

    await db.commit()
    return passport

async def find_global_opportunities(
    user_id: uuid.UUID,
    db: AsyncSession
) -> List[Dict[str, Any]]:
    """
    Finds remote jobs or opportunities using country guides and local PPP ratios.
    """
    stmt = select(TalentPassport).where(TalentPassport.user_id == user_id)
    passport = (await db.execute(stmt)).scalars().first()
    if not passport:
        passport = await generate_talent_passport(user_id, db)

    country = passport.country_code
    country_profile = COUNTRY_HIRING_PROFILES.get(country, COUNTRY_HIRING_PROFILES["IN"])
    ppp = country_profile["ppp_conversion_factor"]

    # Mock/derived remote jobs based on role
    role = passport.verified_role or "Software Developer"
    
    mock_jobs = [
        {"company_name": "GitLab", "role": role, "tier": "tier_1_global", "salary_usd": 90000, "timezone": "UTC-5"},
        {"company_name": "Automattic", "role": role, "tier": "tier_1_global", "salary_usd": 85000, "timezone": "UTC+0"},
        {"company_name": "Zapier", "role": role, "tier": "tier_1_global", "salary_usd": 95000, "timezone": "UTC-8"},
        {"company_name": "Wise", "role": role, "tier": "tier_2_regional", "salary_usd": 70000, "timezone": "UTC+1"},
        {"company_name": "Revolut", "role": role, "tier": "tier_2_regional", "salary_usd": 65000, "timezone": "UTC+0"},
        {"company_name": "Amazon", "role": role, "tier": "tier_3_visa_sponsor", "salary_usd": 120000, "timezone": "UTC-7"}
    ]

    opportunities = []
    for job in mock_jobs:
        # Check eligibility tier
        if job["tier"] not in passport.eligible_company_tiers:
            continue

        # Estimate local PPP salary
        local_salary = job["salary_usd"] * ppp
        
        # Heuristic timezone overlap (IN standard = UTC+5:30)
        timezone_overlap = 80 # default high percentage
        if "UTC-8" in job["timezone"]:
            timezone_overlap = 40
        elif "UTC+1" in job["timezone"] or "UTC+0" in job["timezone"]:
            timezone_overlap = 90

        opportunities.append({
            "company_name": job["company_name"],
            "role": job["role"],
            "hiring_tier": job["tier"],
            "timezone_overlap_percentage": timezone_overlap,
            "salary_usd": job["salary_usd"],
            "salary_localized_ppp": round(local_salary, 2),
            "application_path": "direct" if job["tier"] == "tier_1_global" else "referral_first",
            "visa_type": "None (Remote)" if job["tier"] != "tier_3_visa_sponsor" else "H-1B / Work Visa"
        })

    return opportunities[:20]

async def translate_credential_for_market(
    user_id: uuid.UUID,
    target_market: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Translates candidate profiles for specific foreign job markets.
    """
    stmt = select(TalentPassport).where(TalentPassport.user_id == user_id)
    passport = (await db.execute(stmt)).scalars().first()
    
    cred_stmt = select(SkillCredential).where(SkillCredential.user_id == user_id)
    credential = (await db.execute(cred_stmt)).scalars().first()

    market_contexts = {
        "US": "Tech companies value GitHub activity, system design depth, and LeetCode proficiency",
        "EU": "EU companies value work-life balance signals, GDPR awareness, and open source contributions",
        "UK": "UK companies value communication clarity and structured problem solving narratives",
        "SG": "Singapore values financial technology expertise and regional market awareness",
        "AE": "Dubai/UAE values immediate scale operations, global compliance, and fintech architectures",
        "AU": "Australian tech hubs value agile workflows, systems testing, and collaborative designs"
    }

    m_ctx = market_contexts.get(target_market, "Standard global remote tech markets")
    tier = passport.skill_tier if passport else "silver"
    prs = float(passport.prs_score) if passport and passport.prs_score else 70.0

    prompt = (
        f"Translate this verified skill profile for the {target_market} job market.\n"
        f"Profile parameters: tier={tier}, prs_score={prs}, verified_role={passport.verified_role if passport else 'Software Developer'}.\n"
        f"Market context: {m_ctx}.\n\n"
        f"Provide a JSON response with keys:\n"
        f"- 'professional_summary': A 2-sentence professional summary for {target_market} tech recruiters.\n"
        f"- 'top_dimensions': Three credential dimensions that matter most to {target_market} employers.\n"
        f"- 'key_skills': Three skills to highlight at the top of your profile.\n"
        f"- 'downplay_advice': One specific aspect to downplay or reframe for this market."
    )

    try:
        response = await acall_llm(prompt)
        start_idx = response.find("{")
        end_idx = response.rfind("}")
        return json.loads(response[start_idx:end_idx+1])
    except Exception:
        # Fallback market translation
        return {
            "professional_summary": f"High-performing {passport.verified_role if passport else 'developer'} with a verified place in the top decile of international talent. Specialized in scalable back-end configurations.",
            "top_dimensions": ["Technical Depth", "Problem Solving", "System Thinking"],
            "key_skills": ["Python / FastAPI", "System Design", "SQL Indexing"],
            "downplay_advice": "Focus heavily on direct coding contributions; downplay theoretical coursework or general academic rankings."
        }
