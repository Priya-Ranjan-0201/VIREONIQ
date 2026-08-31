import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy import select
from db.session import async_session_maker, engine
from db.models import JobListing, MarketSignal, Base

async def seed_jobs():
    async with engine.begin() as conn:
        # Create tables if they don't exist (Simple for MVP)
        # In production, use Alembic migrations
        # await conn.run_sync(Base.metadata.create_all)
        pass

    async with async_session_maker() as session:
        # 1. Clear existing jobs for idempotency
        # (Optional, but good for development)
        
        # 2. Seed Market Signals
        signals = [
            MarketSignal(
                role_name="Software Engineer",
                demand_level="High",
                avg_salary=800000,
                trending_skills={"skills": ["React", "Node.js", "AWS", "TypeScript"]}
            ),
            MarketSignal(
                role_name="AI/ML Engineer",
                demand_level="Critical",
                avg_salary=1500000,
                trending_skills={"skills": ["PyTorch", "LLMs", "Vector DBs", "FastAPI"]}
            ),
            MarketSignal(
                role_name="Backend Developer",
                demand_level="Moderate",
                avg_salary=1000000,
                trending_skills={"skills": ["Python", "PostgreSQL", "Docker", "Redis"]}
            )
        ]
        
        for sig in signals:
            existing = (await session.execute(select(MarketSignal).where(MarketSignal.role_name == sig.role_name))).scalars().first()
            if not existing:
                session.add(sig)

        # 3. Seed Job Listings
        jobs = [
            JobListing(
                title="Frontend Developer",
                company_name="Zomato",
                company_tier="Product",
                description="Join the team building India's food delivery giant. Work on high-performance React apps.",
                required_skills="React,TypeScript,Tailwind,Next.js",
                location="Gurugram",
                salary_min=1200000,
                salary_max=2200000,
                is_remote=False,
                job_type="Full-time",
                source="Internal",
                posted_at=datetime.utcnow() - timedelta(days=2),
                competition_index=0.8,
                language_support="English,Hindi"
            ),
            JobListing(
                title="Fullstack Engineer",
                company_name="Vireon Health",
                company_tier="Startup",
                description="Early-stage healthtech startup. Looking for builders who can handle end-to-end features.",
                required_skills="Python,FastAPI,React,PostgreSQL",
                location="Bengaluru",
                salary_min=1500000,
                salary_max=2500000,
                is_remote=True,
                job_type="Full-time",
                source="Internal",
                posted_at=datetime.utcnow() - timedelta(days=1),
                competition_index=0.4,
                language_support="English"
            ),
            JobListing(
                title="Junior Software Engineer",
                company_name="TCS",
                company_tier="Service",
                description="Mass hiring for major digital transformation projects. Open to Tier 2/3 graduates.",
                required_skills="Java,Spring Boot,MySQL,Git",
                location="Pune",
                salary_min=400000,
                salary_max=600000,
                is_remote=False,
                job_type="Full-time",
                source="Internal",
                posted_at=datetime.utcnow() - timedelta(days=5),
                competition_index=0.9,
                language_support="English,Hindi,Marathi"
            ),
            JobListing(
                title="AI Research Intern",
                company_name="Neural Labs",
                company_tier="Startup",
                description="Work on cutting edge RAG pipelines and LLM fine-tuning.",
                required_skills="Python,PyTorch,Transformers,Vector DBs",
                location="Remote",
                salary_min=300000,
                salary_max=500000,
                is_remote=True,
                job_type="Internship",
                source="Internal",
                posted_at=datetime.utcnow() - timedelta(hours=12),
                competition_index=0.6,
                language_support="English"
            ),
            JobListing(
                title="Python Developer (Contract)",
                company_name="SmallBiz Solutions",
                company_tier="Service",
                description="Maintenance of legacy automation scripts and new API development.",
                required_skills="Python,Django,SQL,REST",
                location="Hyderabad",
                salary_min=600000,
                salary_max=900000,
                is_remote=True,
                job_type="Contract",
                source="Internal",
                posted_at=datetime.utcnow() - timedelta(days=10),
                competition_index=0.3,
                language_support="English,Telugu"
            )
        ]
        
        for job in jobs:
            existing = (await session.execute(select(JobListing).where(JobListing.title == job.title, JobListing.company_name == job.company_name))).scalars().first()
            if not existing:
                session.add(job)
        
        await session.commit()
        print("Seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_jobs())
