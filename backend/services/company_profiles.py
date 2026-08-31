"""
Company-specific interview profile definitions and simulator configurations.
Covers TCS, Infosys, Wipro, Cognizant, Flipkart, Amazon, Google, Microsoft, Startups.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import CompanyInterviewProfile
import uuid

COMPANY_PROFILES: Dict[str, Dict[str, Any]] = {
    "tcs": {
        "profile_key": "tcs",
        "display_name": "TCS (Tata Consultancy Services)",
        "company_type": "Service",
        "difficulty_level": "Medium",
        "estimated_ctc_min_lpa": 3.6,
        "estimated_ctc_max_lpa": 7.5,
        "description": "High-volume hiring with focus on core CS fundamentals, coding speed, and general aptitude.",
        "interview_stages": ["Aptitude Test", "Technical Interview", "HR Round"],
        "question_style_weights": {"DSA": 0.4, "Behavioral": 0.3, "System Design": 0.1, "Core CS": 0.2},
        "evaluation_criteria": ["Aptitude Score", "Coding Correctness", "Communication Clarity"],
        "leadership_principles": None
    },
    "infosys": {
        "profile_key": "infosys",
        "display_name": "Infosys",
        "company_type": "Service",
        "difficulty_level": "Medium",
        "estimated_ctc_min_lpa": 3.6,
        "estimated_ctc_max_lpa": 8.0,
        "description": "Recruits for system engineer and specialist programmer tracks. Tests fundamentals, problem solving, and analytical thinking.",
        "interview_stages": ["InfyTQ Exam", "Technical Evaluation", "Behavioral Interview"],
        "question_style_weights": {"DSA": 0.5, "Behavioral": 0.2, "System Design": 0.1, "Core CS": 0.2},
        "evaluation_criteria": ["Logical Reasoning", "Coding Efficiency", "Professional Adaptability"],
        "leadership_principles": None
    },
    "wipro": {
        "profile_key": "wipro",
        "display_name": "Wipro",
        "company_type": "Service",
        "difficulty_level": "Medium",
        "estimated_ctc_min_lpa": 3.5,
        "estimated_ctc_max_lpa": 7.0,
        "description": "Mass recruitment with focus on basic coding, OOPs principles, SQL, and database concepts.",
        "interview_stages": ["Online Assessment", "Technical Panel", "HR Interview"],
        "question_style_weights": {"DSA": 0.3, "Behavioral": 0.4, "System Design": 0.1, "Core CS": 0.2},
        "evaluation_criteria": ["Coding Aptitude", "OOPs Concepts", "Teamwork Dynamics"],
        "leadership_principles": None
    },
    "amazon": {
        "profile_key": "amazon",
        "display_name": "Amazon",
        "company_type": "FAANG",
        "difficulty_level": "Hard",
        "estimated_ctc_min_lpa": 18.0,
        "estimated_ctc_max_lpa": 45.0,
        "description": "Extremely rigorous DSA evaluation combined with deep dive into Amazon's Leadership Principles.",
        "interview_stages": ["Online Assessment", "Technical Phone Screen", "Loop (3x Tech, 1x System Design)"],
        "question_style_weights": {"DSA": 0.5, "Behavioral": 0.3, "System Design": 0.2},
        "evaluation_criteria": ["Analytical Ability", "System Design Scalability", "Leadership Principle Alignment"],
        "leadership_principles": [
            "Customer Obsession", "Ownership", "Invent and Simplify", "Are Right, A Lot",
            "Learn and Be Curious", "Hire and Develop the Best", "Insist on the Highest Standards",
            "Think Big", "Bias for Action", "Frugality", "Earn Trust", "Dive Deep",
            "Have Backbone; Disagree and Commit", "Deliver Results"
        ]
    },
    "google": {
        "profile_key": "google",
        "display_name": "Google",
        "company_type": "FAANG",
        "difficulty_level": "Expert",
        "estimated_ctc_min_lpa": 22.0,
        "estimated_ctc_max_lpa": 55.0,
        "description": "Evaluation of complex data structures, algorithms, system design, and Googleyness.",
        "interview_stages": ["Phone Screen", "Onsite Loop (4x Coding, 1x System Design / Googlyness)"],
        "question_style_weights": {"DSA": 0.6, "Behavioral": 0.2, "System Design": 0.2},
        "evaluation_criteria": ["General Cognitive Ability", "Role-Related Knowledge", "Coding & Logic", "Googleyness"],
        "leadership_principles": None
    },
    "microsoft": {
        "profile_key": "microsoft",
        "display_name": "Microsoft",
        "company_type": "FAANG",
        "difficulty_level": "Hard",
        "estimated_ctc_min_lpa": 16.0,
        "estimated_ctc_max_lpa": 40.0,
        "description": "DSA, design patterns, operating systems, and general software architecture.",
        "interview_stages": ["Coding Assessment", "Collaborative Design Round", "Technical Loop", "AA (As Appropriate) Round"],
        "question_style_weights": {"DSA": 0.5, "Behavioral": 0.2, "System Design": 0.3},
        "evaluation_criteria": ["Problem Solving", "Design Patterns", "Collaborative Alignment"],
        "leadership_principles": None
    },
    "flipkart": {
        "profile_key": "flipkart",
        "display_name": "Flipkart",
        "company_type": "Product",
        "difficulty_level": "Hard",
        "estimated_ctc_min_lpa": 14.0,
        "estimated_ctc_max_lpa": 32.0,
        "description": "Machine coding round (Lld) followed by standard DSA and System Design evaluations.",
        "interview_stages": ["Machine Coding Round", "DSA Evaluation", "System Design (Hld)", "HM Behavioral Round"],
        "question_style_weights": {"DSA": 0.4, "Behavioral": 0.2, "System Design": 0.4},
        "evaluation_criteria": ["Extensible Code Structure", "Algorithm Optimality", "High-Level Architecture"],
        "leadership_principles": None
    },
    "startups": {
        "profile_key": "startups",
        "display_name": "High-Growth Startups",
        "company_type": "Startup",
        "difficulty_level": "Hard",
        "estimated_ctc_min_lpa": 8.0,
        "estimated_ctc_max_lpa": 25.0,
        "description": "Practical software development capabilities, rapid prototyping, versatility, and adaptability.",
        "interview_stages": ["Take-Home Assignment", "Assignment Review Walkthrough", "System Design & Scale", "Founder's Chat"],
        "question_style_weights": {"DSA": 0.2, "Behavioral": 0.3, "System Design": 0.5},
        "evaluation_criteria": ["Ship Speed & Clean Code", "Scalability intuition", "Growth mindset & resilience"],
        "leadership_principles": None
    }
}


async def seed_company_profiles_if_empty(db: AsyncSession) -> None:
    """Populate database table with target company profiles if empty."""
    for key, p in COMPANY_PROFILES.items():
        stmt = select(CompanyInterviewProfile).where(CompanyInterviewProfile.profile_key == key)
        exists = (await db.execute(stmt)).scalar_one_or_none()
        if not exists:
            new_profile = CompanyInterviewProfile(
                profile_key=key,
                display_name=p["display_name"],
                company_type=p["company_type"],
                interview_stages=p["interview_stages"],
                question_style_weights=p["question_style_weights"],
                evaluation_criteria=p["evaluation_criteria"],
                leadership_principles=p["leadership_principles"],
                difficulty_level=p["difficulty_level"],
                estimated_ctc_min_lpa=p["estimated_ctc_min_lpa"],
                estimated_ctc_max_lpa=p["estimated_ctc_max_lpa"],
                description=p["description"]
            )
            db.add(new_profile)
    await db.commit()


async def get_company_profiles(db: AsyncSession) -> List[CompanyInterviewProfile]:
    """Retrieve all active company interview profiles."""
    await seed_company_profiles_if_empty(db)
    stmt = select(CompanyInterviewProfile).where(CompanyInterviewProfile.is_active == True)
    return list((await db.execute(stmt)).scalars().all())


async def get_company_profile_by_key(db: AsyncSession, key: str) -> Optional[CompanyInterviewProfile]:
    """Retrieve details of a single company profile by its key."""
    stmt = select(CompanyInterviewProfile).where(CompanyInterviewProfile.profile_key == key)
    return (await db.execute(stmt)).scalar_one_or_none()
