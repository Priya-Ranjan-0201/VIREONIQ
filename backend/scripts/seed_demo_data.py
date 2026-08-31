import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from db.session import async_session_maker
from db.models import User, Resume, ResumeScore, GapAnalysis, Application, JobListing

async def seed_demo_data() -> None:
    """
    Seed demo data for the test user (test@example.com).

    Creates a sample Resume with a ResumeScore, a GapAnalysis record, and
    up to three Application rows linked to existing JobListings.  Requires
    seed_user.py to have been run first so the test user already exists.
    The function is safely idempotent for the role / user lookup step but
    will append new records on repeated runs, so it is intended for
    development / staging environments only.
    """
    print("Seeding demo data for test@example.com...")
    async with async_session_maker() as session:
        # 1. Get the test user
        stmt = select(User).where(User.email == 'test@example.com')
        user_obj = (await session.execute(stmt)).scalars().first()
        user_id = user_obj.id if user_obj else None
        
        if not user_id:
            print("Test user not found. Please run seed_user.py first.")
            return

        # 2. Add a mock Resume and Score
        resume = Resume(
            user_id=user_id,
            storage_key="resumes/demo_resume.pdf",
            mime_type="application/pdf",
            parsed_data={"summary": "Experienced Software Engineer with 5 years in Python and React."}
        )
        session.add(resume)
        await session.flush()
        
        score = ResumeScore(
            resume_id=resume.id,
            overall_score=82.5,
            formatting_score=90.0,
            improvement_notes={"formatting": "Excellent", "keywords": "Python, React, AWS"}
        )
        session.add(score)

        # 3. Add a Gap Analysis
        gap = GapAnalysis(
            user_id=user_id,
            target_role_name="Senior Software Engineer",
            overall_readiness_score=74.0,
            technical_gap_score=65.0,
            communication_gap_score=80.0
        )
        session.add(gap)

        # 4. Add some Applications
        stmt = select(JobListing.id).limit(3)
        job_ids = list((await session.execute(stmt)).scalars().all())
        
        if job_ids:
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
