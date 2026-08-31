import math
import uuid
import json
from datetime import datetime, date, timedelta, timezone
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.llm.orchestrator import acall_llm
from core.security import check_prompt_injection
from db.models import User, CareerRebirthPlan, TargetRole, Resume

TRANSFERABLE_SKILL_MAP = {
    "banking_finance": {
        "transferable_to": ["fintech_analyst", "data_analyst", "product_manager_fintech", "backend_developer_banking"],
        "strong_transfers": ["analytical_thinking", "risk_assessment", "data_interpretation", "regulatory_knowledge", "process_optimization"],
        "reframe_narratives": {
            "risk_assessment": "debugging and system reliability thinking",
            "regulatory_knowledge": "compliance engineering and audit systems",
            "data_interpretation": "SQL analytics and business intelligence"
        }
    },
    "teaching_education": {
        "transferable_to": ["edtech_engineer", "technical_writer", "product_manager_edtech", "developer_advocate", "UX_researcher"],
        "strong_transfers": ["curriculum_design", "communication", "patience_debugging", "breaking_complex_concepts", "assessment_design"],
        "reframe_narratives": {
            "curriculum_design": "system design and learning flow architecture",
            "assessment_design": "test engineering and quality assurance mindset"
        }
    },
    "logistics_operations": {
        "transferable_to": ["backend_developer", "data_engineer", "supply_chain_analyst", "platform_engineer"],
        "strong_transfers": ["systems_thinking", "optimization", "coordination", "process_mapping", "deadline_management"],
        "reframe_narratives": {
            "systems_thinking": "distributed backend pipeline design",
            "optimization": "algorithm time-space complexity tuning"
        }
    },
    "healthcare_nursing": {
        "transferable_to": ["healthtech_engineer", "data_analyst_health", "product_manager_health"],
        "strong_transfers": ["attention_to_detail", "protocol_following", "critical_decision_making", "patient_data_handling", "shift_under_pressure"],
        "reframe_narratives": {
            "protocol_following": "strict schema design and API contract compliance",
            "attention_to_detail": "robust unit testing and edge case debugging"
        }
    },
    "military_defense": {
        "transferable_to": ["cybersecurity_analyst", "project_manager", "devops_engineer", "platform_reliability_engineer"],
        "strong_transfers": ["discipline", "security_mindset", "team_coordination", "high_stakes_decision_making", "hardware_familiarity"],
        "reframe_narratives": {
            "security_mindset": "zero-trust application security and pen-testing",
            "high_stakes_decision_making": "incident response and site reliability engineering"
        }
    },
    "sales_marketing": {
        "transferable_to": ["growth_engineer", "product_manager", "data_analyst_marketing", "developer_advocate"],
        "strong_transfers": ["user_empathy", "metrics_driven_thinking", "communication", "A_B_testing_mindset", "funnel_thinking"],
        "reframe_narratives": {
            "A_B_testing_mindset": "feature flag systems and user clickstream telemetry",
            "funnel_thinking": "system throughput and performance bottlenecks"
        }
    }
}

CAREER_BREAK_PENALTY_NULLIFIER_MAP = {
    "maternity_paternity": "project portfolio built during break",
    "health": "certifications completed during recovery",
    "family_care": "freelance or open source contributions",
    "travel": "international perspective and adaptability signal",
    "self_study": "direct evidence of self-directed learning",
    "startup_failed": "founder experience, high-level business execution and system ownership"
}

# Hours to learn typical tech skills from scratch
SKILL_LEARNING_HOURS = {
    "Python": 40,
    "FastAPI": 30,
    "React": 50,
    "TypeScript": 30,
    "SQL": 20,
    "PostgreSQL": 20,
    "System Design": 60,
    "Docker": 15,
    "Kubernetes": 40,
    "Data Structures": 80,
    "Algorithms": 80
}

async def extract_transferable_skills(
    background_text: str,
    current_domain: str,
    target_role: str
) -> Dict[str, Any]:
    """
    Analyzes background text and extracts transferable skills and reframes them for a tech role.
    """
    if check_prompt_injection(background_text):
        raise ValueError("Prompt injection detected in input.")

    domain_map = TRANSFERABLE_SKILL_MAP.get(current_domain, {})
    prompt = (
        f"Analyze this professional background and extract transferable skills for a transition to {target_role}. "
        f"Background: {background_text}. Domain context: {domain_map}. "
        f"For each identified transferable skill: "
        f"1. Name the original skill as the person would describe it. "
        f"2. Name the tech equivalent that a hiring manager recognizes. "
        f"3. Write one sentence reframing it as a tech strength (active voice, specific). "
        f"4. Rate transfer strength as High, Medium, or Low. "
        f"5. Name one concrete project that would demonstrate this transfer in 4 weeks. "
        f"Format your response as a valid JSON containing a key 'skills' pointing to a list of these objects."
    )
    
    try:
        response = await acall_llm(prompt)
        # Parse json from response
        # Find start of json list or dict
        start_idx = response.find("{")
        end_idx = response.rfind("}")
        parsed_data = json.loads(response[start_idx:end_idx+1])
        return parsed_data
    except Exception:
        # Heuristic fallback
        skills = []
        strongs = domain_map.get("strong_transfers", ["analytical_thinking", "process_optimization"])
        narratives = domain_map.get("reframe_narratives", {})
        for s in strongs:
            tech_eq = narratives.get(s, f"advanced tech execution in {s}")
            skills.append({
                "original_skill": s.replace("_", " ").title(),
                "tech_equivalent": tech_eq,
                "reframe_sentence": f"Leverages extensive experience in {s.replace('_', ' ')} to architect scalable solutions.",
                "transfer_strength": "High",
                "concrete_project": f"Build a mock system demonstrating {s.replace('_', ' ')} logic in Python."
            })
        return {"skills": skills}

async def generate_transition_roadmap(
    user_id: uuid.UUID,
    current_domain: str,
    target_role: str,
    available_hours_per_week: float,
    career_break_reason: Optional[str],
    break_duration_months: Optional[int],
    db: AsyncSession
) -> CareerRebirthPlan:
    """
    Generates a personalized, highly structured 6-phase roadmap for a career switcher or returner.
    """
    # 1. Fetch transferable skills
    # Simple default summary description for LLM
    fallback_background = f"Transitioning from {current_domain} to {target_role}."
    skills_analysis = await extract_transferable_skills(fallback_background, current_domain, target_role)
    transferable_skills = skills_analysis.get("skills", [])

    # 2. Determine break strategist
    break_strategy = None
    if break_duration_months and break_duration_months > 0 and career_break_reason:
        break_strategy = CAREER_BREAK_PENALTY_NULLIFIER_MAP.get(
            career_break_reason, "custom portfolio building showing active tech progression"
        )

    # 3. Calculate realistic timeline
    # Determine what skills we need to learn (mock difference)
    target_role_stmt = select(TargetRole).where(TargetRole.role_name.ilike(f"%{target_role}%"))
    role = (await db.execute(target_role_stmt)).scalars().first()
    required_skills = role.required_skills if role and role.required_skills else ["Python", "FastAPI", "SQL", "System Design"]

    # Exclude skills already transferred
    transferred_names = [s["original_skill"].lower() for s in transferable_skills]
    skills_to_learn = [s for s in required_skills if s.lower() not in transferred_names]
    
    total_hours = sum(SKILL_LEARNING_HOURS.get(s, 30) for s in skills_to_learn)
    weeks_needed = max(4, math.ceil(total_hours / max(1.0, available_hours_per_week)))
    completion_target_date = date.today() + timedelta(weeks=weeks_needed)

    # Build 6 phases
    phases = [
        {
            "phase": 1,
            "title": "Foundation Sprint",
            "weeks": f"1-{max(1, weeks_needed // 6)}",
            "goal": "Build the minimum viable skill set to speak the language of your target role",
            "daily_tasks": [f"Study fundamentals of {s}" for s in skills_to_learn[:2]],
            "milestone": f"Complete one small project combining {current_domain} logic with {skills_to_learn[0] if skills_to_learn else 'Python'}",
            "break_nullifier": break_strategy
        },
        {
            "phase": 2,
            "title": "Portfolio Construction",
            "weeks": f"{weeks_needed // 6 + 1}-{weeks_needed // 3}",
            "goal": f"Build 2 projects that showcase {current_domain} advantage in {target_role}",
            "project_ideas": [
                f"A database-intensive application simulating {current_domain} workflows built on FastAPI.",
                f"Analytics dashboard showcasing data flows relevant to {current_domain} metrics."
            ],
            "milestone": "Deploy both projects to GitHub with interactive live demo URLs"
        },
        {
            "phase": 3,
            "title": "Interview Language Acquisition",
            "weeks": f"{weeks_needed // 3 + 1}-{weeks_needed // 2}",
            "goal": "Speak the exact language hiring managers in your target role use",
            "placeiq_sessions": "Start 5 PlaceIQ simulation sessions, focusing on technical depth.",
            "story_work": "Draft 5 stories reframing original domain accomplishments as tech project assets."
        },
        {
            "phase": 4,
            "title": "Network Activation",
            "weeks": f"{weeks_needed // 2 + 1}-{2 * weeks_needed // 3}",
            "goal": "Connect with professionals who transitioned successfully",
            "search_query": f"LinkedIn: '{current_domain} to {target_role}'",
            "outreach_angle": "Use shared transition background to request 15-minute coffee chats."
        },
        {
            "phase": 5,
            "title": "Application Sprint",
            "weeks": f"{2 * weeks_needed // 3 + 1}-{weeks_needed}",
            "goal": "Target companies that heavily value your specific domain background",
            "target_company_types": TRANSFERABLE_SKILL_MAP.get(current_domain, {}).get("transferable_to", ["product_companies"]),
            "resume_frame": "Structure resume to highlight domain advantage at the top."
        },
        {
            "phase": 6,
            "title": "Offer Negotiation",
            "weeks": f"{weeks_needed}+",
            "goal": "Position domain experience to negotiate premium bands",
            "leverage_points": f"Your background in {current_domain} represents domain expertise that other candidates lack."
        }
    ]

    # Save to SQL database
    plan_stmt = select(CareerRebirthPlan).where(CareerRebirthPlan.user_id == user_id)
    plan = (await db.execute(plan_stmt)).scalars().first()
    
    if not plan:
        plan = CareerRebirthPlan(user_id=user_id)
        db.add(plan)

    plan.current_domain = current_domain
    plan.target_role = target_role
    plan.career_break_reason = career_break_reason
    plan.break_duration_months = break_duration_months
    plan.available_hours_per_week = available_hours_per_week
    plan.weeks_to_completion = weeks_needed
    plan.completion_target_date = datetime.combine(completion_target_date, datetime.min.time(), tzinfo=timezone.utc)
    plan.phases = phases
    plan.transferable_skills = transferable_skills
    plan.break_nullifier_strategy = break_strategy

    await db.commit()
    return plan

async def rewrite_resume_for_transition(
    resume_id: uuid.UUID,
    target_role: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Rewrites a transitioner's resume to position their past non-tech domain experience as a unique strength.
    """
    stmt = select(Resume).where(Resume.id == resume_id)
    resume = (await db.execute(stmt)).scalars().first()
    if not resume:
        raise ValueError("Resume not found.")

    resume_text = resume.parsed_data.get("text", "") if resume.parsed_data else ""
    if not resume_text:
        # Fallback raw text placeholder
        resume_text = "Experienced Professional in Customer Service and Sales Operations."

    prompt = (
        f"Rewrite this resume for someone transitioning to {target_role}.\n"
        f"Resume text: {resume_text}\n"
        f"Rules:\n"
        f"- Lead the summary with their domain expertise framed as a major tech asset.\n"
        f"- Add a 'Domain Advantage' section with 3 bullet points showing how their background gives them an edge.\n"
        f"- Reframe experience bullets using strong technical action verbs.\n"
        f"- Return a JSON containing the keys: 'summary_rewritten', 'domain_advantage_section' (list of 3 bullets), "
        f"'experience_bullets_rewritten' (dict mapping original sentences to rewritten ones)."
    )

    try:
        response = await acall_llm(prompt)
        start_idx = response.find("{")
        end_idx = response.rfind("}")
        return json.loads(response[start_idx:end_idx+1])
    except Exception:
        # Fallback rewrite
        return {
            "summary_rewritten": f"Forward-looking professional bringing deep domain insight to {target_role} challenges. Expert at implementing process optimizations and data pipelines.",
            "domain_advantage_section": [
                f"Deep domain expertise allowing faster requirements analysis for {target_role} configurations.",
                "Proven record of metric-driven optimization under pressure.",
                "Strong cross-functional communication bridging technical and business teams."
            ],
            "experience_bullets_rewritten": {
                "Managed day-to-day operations and team schedules": f"Architected task scheduling and resource allocation systems to optimize operational throughput.",
                "Communicated with clients and resolved issues": "Engaged in stakeholder requirements gathering and reduced client onboarding churn via structured feedback loops."
            },
            "skills_to_add": ["FastAPI", "Python", "SQL", "System Design"]
        }
