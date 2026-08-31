from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from db.models import User, JobListing, JobMatch, Resume, InterviewScore, GapAnalysis, UserPreference
from . import filters, scorer, ranker, explainability

async def get_job_recommendations(
    db: AsyncSession, 
    user: User, 
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Modular Recommendation Pipeline (Module 5)
    1. Filter
    2. Score
    3. Rank (Probability aware)
    4. Explain
    """
    
    # 1. Fetch User Data
    resume = (await db.execute(
        select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc())
    )).scalars().first()
    
    prefs = (await db.execute(
        select(UserPreference).where(UserPreference.user_id == user.id)
    )).scalars().first()
    
    latest_interview = (await db.execute(
        select(InterviewScore).join(InterviewScore.session).where(InterviewScore.session.has(user_id=user.id)).order_by(InterviewScore.created_at.desc())
    )).scalars().first()
    
    gap_analysis = (await db.execute(
        select(GapAnalysis).where(GapAnalysis.user_id == user.id).order_by(GapAnalysis.created_at.desc())
    )).scalars().first()

    # 2. Layer 1: Apply Filters
    all_jobs = list((await db.execute(select(JobListing).limit(100))).scalars().all())
    if not all_jobs:
        from datetime import datetime, timedelta, timezone
        seed_jobs_list = [
            JobListing(
                title="Software Engineer (L3 / SDE-1)",
                company_name="Google",
                company_tier="Tier-1 MNC",
                description="Join Google's Core Infrastructure & Search engineering teams. Design and scale distributed systems serving billions of queries.",
                required_skills="Go,C++,Python,Distributed Systems,Algorithms",
                location="Bengaluru",
                salary_min=2400000,
                salary_max=4200000,
                is_remote=False,
                job_type="Full-time",
                source="Campus / Direct Referral",
                posted_at=datetime.now(timezone.utc) - timedelta(days=1),
                competition_index=0.85,
                language_support="English"
            ),
            JobListing(
                title="Software Development Engineer I",
                company_name="Amazon",
                company_tier="Tier-1 MNC",
                description="Build high-concurrency order fulfillment and AWS cloud orchestration systems with sub-100ms latency SLAs.",
                required_skills="Java,AWS,Object-Oriented Design,Spring Boot,MySQL",
                location="Hyderabad",
                salary_min=2200000,
                salary_max=3200000,
                is_remote=False,
                job_type="Full-time",
                source="Direct Portal",
                posted_at=datetime.now(timezone.utc) - timedelta(days=2),
                competition_index=0.88,
                language_support="English"
            ),
            JobListing(
                title="Backend Infrastructure Engineer",
                company_name="Stripe",
                company_tier="Top Product MNC",
                description="Architect zero-duplicate payment dispatch pipelines, idempotency layers, and ledger reconciliation systems.",
                required_skills="Python,Go,Kafka,PostgreSQL,Distributed Systems",
                location="Remote (India)",
                salary_min=2800000,
                salary_max=4800000,
                is_remote=True,
                job_type="Full-time",
                source="Referral Pipeline",
                posted_at=datetime.now(timezone.utc) - timedelta(days=1),
                competition_index=0.75,
                language_support="English"
            ),
            JobListing(
                title="SDE-1 / SDE-2 (Real-Time Logistics)",
                company_name="Flipkart",
                company_tier="Top Product MNC",
                description="Engineering high-scale inventory locks and flash-sale checkout engines handling 10,000+ orders/second.",
                required_skills="Java,Spring Boot,Redis,Kafka,System Design",
                location="Bengaluru",
                salary_min=1800000,
                salary_max=2800000,
                is_remote=False,
                job_type="Full-time",
                source="Direct Portal",
                posted_at=datetime.now(timezone.utc) - timedelta(days=3),
                competition_index=0.82,
                language_support="English,Hindi"
            ),
            JobListing(
                title="Full-Stack Engineer (Platform)",
                company_name="Swiggy",
                company_tier="High-Growth Startup",
                description="Build real-time delivery tracking, high-throughput delivery partner assignment, and consumer web applications.",
                required_skills="TypeScript,React,Go,PostgreSQL,Docker",
                location="Bengaluru",
                salary_min=1600000,
                salary_max=2600000,
                is_remote=False,
                job_type="Full-time",
                source="Direct Referral",
                posted_at=datetime.now(timezone.utc) - timedelta(days=2),
                competition_index=0.79,
                language_support="English,Hindi"
            ),
            JobListing(
                title="High-Throughput Core Systems Engineer",
                company_name="Zepto",
                company_tier="High-Growth Startup",
                description="Scale 10-minute quick-commerce dark store routing and inventory reservation algorithms with millisecond precision.",
                required_skills="Go,Python,Redis,Kubernetes,gRPC",
                location="Mumbai",
                salary_min=1500000,
                salary_max=2500000,
                is_remote=False,
                job_type="Full-time",
                source="Direct Portal",
                posted_at=datetime.now(timezone.utc) - timedelta(days=1),
                competition_index=0.72,
                language_support="English"
            ),
            JobListing(
                title="FinTech Payment Gateway Engineer",
                company_name="Razorpay",
                company_tier="FinTech & HFT",
                description="Develop seamless multi-currency checkout gateways and bank integration protocols with 99.999% uptime.",
                required_skills="Python,Go,MySQL,Redis,System Architecture",
                location="Bengaluru",
                salary_min=1800000,
                salary_max=3000000,
                is_remote=True,
                job_type="Full-time",
                source="Direct Referral",
                posted_at=datetime.now(timezone.utc) - timedelta(days=4),
                competition_index=0.80,
                language_support="English"
            ),
            JobListing(
                title="Cloud Infrastructure & Systems Engineer",
                company_name="Microsoft",
                company_tier="Tier-1 MNC",
                description="Work on Microsoft Azure core compute platforms, virtualization layers, and edge telemetry pipelines.",
                required_skills="C#,C++,Azure,Kubernetes,Linux Internals",
                location="Hyderabad",
                salary_min=2000000,
                salary_max=3000000,
                is_remote=False,
                job_type="Full-time",
                source="Campus / Direct Referral",
                posted_at=datetime.now(timezone.utc) - timedelta(days=3),
                competition_index=0.84,
                language_support="English"
            )
        ]
        for sj in seed_jobs_list:
            db.add(sj)
        await db.commit()
        all_jobs = seed_jobs_list

    filtered_jobs = filters.apply_hard_filters(list(all_jobs), prefs)
    if not filtered_jobs:
        filtered_jobs = list(all_jobs)

    # 3. Layer 2, 3 & 4: Score, Rank, and Explain
    scored_matches = []
    for job in filtered_jobs:
        # Layer 2: Base Scorer
        base_scores = scorer.get_base_scores(user, job, resume, latest_interview, gap_analysis)
        
        # Layer 3: Ranking (Skill Fit vs Offer Probability)
        offer_prob = ranker.calculate_offer_probability(
            base_scores["skill_fit"], 
            job, 
            base_scores["interview_fit"]
        )
        
        confidence = ranker.get_confidence_level(base_scores["final_match_score"])
        
        # Layer 4: Explainability
        explanation = explainability.generate_match_explanation(
            user, job, resume, latest_interview, base_scores
        )
        
        scored_matches.append({
            "job": job,
            "match_score": base_scores["final_match_score"],
            "skill_fit_score": base_scores["skill_fit"],
            "offer_probability_score": offer_prob,
            "confidence_level": confidence,
            "explanation": explanation,
            "salary_band": await predict_salary_band(job, base_scores["final_match_score"])
        })

    # Sort by final match score descending
    scored_matches.sort(key=lambda x: x["match_score"], reverse=True)
    return scored_matches[:limit]

async def predict_salary_band(job: JobListing, user_score: float) -> str:
    """Predict salary band with confidence factoring."""
    base_min = job.salary_min or 500000
    base_max = job.salary_max or 1200000
    
    # Multiplier based on score (0.8 to 1.2)
    multiplier = 0.8 + (user_score / 100) * 0.4
    
    pred_min = base_min * multiplier
    pred_max = base_max * multiplier
    
    # India specific formatting (Lakhs)
    return f"₹{round(pred_min/100000, 1)}L - ₹{round(pred_max/100000, 1)}L"
