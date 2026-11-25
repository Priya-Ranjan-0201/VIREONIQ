import asyncio
from datetime import datetime
from sqlalchemy import select
from core.config import settings
from db.session import async_session_maker
from db.models import User, Resume, ResumeScore, GapAnalysis, Application, JobListing

async def seed_demo_data() -> None:
    """
    Seed demo data for local dev test users (development/staging only).
    """
    if settings.is_production:
        raise RuntimeError("Refusing to run seed_demo_data() in production environment.")
    print("Seeding demo data for dev users...")
    async with async_session_maker() as session:
        for target_email in ['test@example.com', 'demo@vireoniq.com']:
            stmt = select(User).where(User.email == target_email)
            user_obj = (await session.execute(stmt)).scalars().first()
            if not user_obj:
                continue
            user_id = user_obj.id

            # Check if user already has a resume
            res_stmt = select(Resume).where(Resume.user_id == user_id)
            existing_resume = (await session.execute(res_stmt)).scalars().first()
            if not existing_resume:
                resume = Resume(
                    user_id=user_id,
                    storage_key=f"resumes/demo_resume_{user_id}.pdf",
                    mime_type="application/pdf",
                    parsed_data={
                        "summary": "Full Stack Senior Engineer with 5+ years experience in Python, TypeScript, React, PostgreSQL, Docker, Microservices.",
                        "skills": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "AWS", "System Design"],
                        "experience_years": 5.5,
                    }
                )
                session.add(resume)
                await session.flush()
                
                score = ResumeScore(
                    resume_id=resume.id,
                    overall_score=88.0,
                    formatting_score=92.0,
                    improvement_notes={"formatting": "Strong hierarchy", "keywords": "Python, React, AWS, Microservices"}
                )
                session.add(score)

            # Check if user already has gap analysis
            gap_stmt = select(GapAnalysis).where(GapAnalysis.user_id == user_id)
            existing_gap = (await session.execute(gap_stmt)).scalars().first()
            if not existing_gap:
                gap = GapAnalysis(
                    user_id=user_id,
                    target_role_name="Senior Software Engineer",
                    overall_readiness_score=78.5,
                    technical_gap_score=68.0,
                    communication_gap_score=85.0
                )
                session.add(gap)

            # Check applications
            app_stmt = select(Application).where(Application.user_id == user_id)
            existing_app = (await session.execute(app_stmt)).scalars().first()
            if not existing_app:
                stmt_jobs = select(JobListing.id).limit(3)
                job_ids = list((await session.execute(stmt_jobs)).scalars().all())
                statuses = ["applied", "interview", "oa"]
                for i, job_id in enumerate(job_ids):
                    app = Application(
                        user_id=user_id,
                        job_id=job_id,
                        status=statuses[i % len(statuses)],
                        applied_at=datetime.utcnow()
                    )
                    session.add(app)

        await session.commit()
    print("Demo data seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_demo_data())
