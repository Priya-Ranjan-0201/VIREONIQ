import asyncio
import uuid
import json
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from db.session import async_session_maker, engine
from db.models import (
    User, Role, Profile, StudentProfile, UserPremiumStatus,
    EarnToLearnLedger, ParentLink, MoodCheckin, FacultyClass,
    FacultyClassStudent, InterviewSession, InterviewScore,
    VernacularConcept, OfflineBundle, StudyGroupSession, PeerFeedback
)
from core.security import get_password_hash

async def seed_resilience_demo() -> None:
    print("Seeding full resilience telemetry data...")
    async with async_session_maker() as session:
        # 1. Ensure Roles exist
        role_map = {}
        for role_name in ["User", "Admin", "Recruiter"]:
            stmt = select(Role).where(Role.name == role_name)
            role = (await session.execute(stmt)).scalars().first()
            if not role:
                role = Role(name=role_name, description=f"{role_name} role")
                session.add(role)
                await session.flush()
            role_map[role_name] = role.id

        # 2. Get/Promote Test User to Admin (so they can access both student and faculty dashboards)
        stmt = select(User).where(User.email == "test@example.com")
        test_user = (await session.execute(stmt)).scalars().first()
        if not test_user:
            test_user = User(
                email="test@example.com",
                password_hash=get_password_hash("password"),
                role_id=role_map["Admin"],
                is_active=True,
                is_email_verified=True
            )
            session.add(test_user)
            await session.flush()
        else:
            test_user.role_id = role_map["Admin"]
            
        user_id = test_user.id

        # Ensure Profile for Test User
        prof_stmt = select(Profile).where(Profile.user_id == user_id)
        test_profile = (await session.execute(prof_stmt)).scalars().first()
        if not test_profile:
            test_profile = Profile(
                user_id=user_id,
                first_name="Candidate",
                last_name="Test",
                phone="919876543210",
                target_role="Software Developer",
                target_company_type="Product",
                education_tier="tier3",
                placement_readiness_score=78.5
            )
            session.add(test_profile)
        else:
            test_profile.placement_readiness_score = 78.5

        # Ensure StudentProfile for Test User
        sp_stmt = select(StudentProfile).where(StudentProfile.user_id == user_id)
        test_sp = (await session.execute(sp_stmt)).scalars().first()
        if not test_sp:
            test_sp = StudentProfile(
                user_id=user_id,
                college_name="State Engineering College",
                graduation_year=2026,
                degree="B.Tech",
                branch="Computer Science",
                cgpa=8.5,
                onboarding_step=3,
                placement_readiness_score=78.5,
                acquisition_channel="whatsapp_organic"
            )
            session.add(test_sp)
        else:
            test_sp.placement_readiness_score = 78.5

        # 3. Premium Status & Ledger
        prem_stmt = select(UserPremiumStatus).where(UserPremiumStatus.user_id == user_id)
        premium = (await session.execute(prem_stmt)).scalars().first()
        if not premium:
            premium = UserPremiumStatus(
                user_id=user_id,
                premium_until=datetime.utcnow() + timedelta(days=45),
                source="earn_to_learn"
            )
            session.add(premium)
        else:
            premium.premium_until = datetime.utcnow() + timedelta(days=45)

        # Ledger entries
        ledger_stmt = select(EarnToLearnLedger).where(EarnToLearnLedger.user_id == user_id)
        existing_ledgers = (await session.execute(ledger_stmt)).scalars().all()
        if not existing_ledgers:
            ledger1 = EarnToLearnLedger(
                user_id=user_id,
                contribution_type="translation",
                reference_id=uuid.uuid4(),
                premium_days=15,
                status="approved"
            )
            ledger2 = EarnToLearnLedger(
                user_id=user_id,
                contribution_type="debrief",
                reference_id=uuid.uuid4(),
                premium_days=30,
                status="approved"
            )
            session.add_all([ledger1, ledger2])

        # 4. Parent Link
        parent_stmt = select(ParentLink).where(ParentLink.student_id == user_id)
        parent = (await session.execute(parent_stmt)).scalars().first()
        if not parent:
            parent = ParentLink(
                student_id=user_id,
                parent_phone="919111222333",
                parent_name="Parent Guardian",
                consent_status="active",
                consent_requested_at=datetime.utcnow() - timedelta(days=10),
                consented_at=datetime.utcnow() - timedelta(days=9)
            )
            session.add(parent)

        # 5. Mood Check-ins
        mood_stmt = select(MoodCheckin).where(MoodCheckin.user_id == user_id)
        existing_moods = (await session.execute(mood_stmt)).scalars().all()
        if not existing_moods:
            for d in range(5):
                checkin = MoodCheckin(
                    user_id=user_id,
                    mood_value=["positive", "neutral", "positive", "low", "neutral"][d],
                    checked_in_at=datetime.utcnow() - timedelta(days=4-d)
                )
                session.add(checkin)

        # 6. Seed Faculty Class & Mock Students
        class_stmt = select(FacultyClass).where(FacultyClass.faculty_id == user_id)
        test_class = (await session.execute(class_stmt)).scalars().first()
        if not test_class:
            test_class = FacultyClass(
                faculty_id=user_id,
                class_name="CS-A Placement Batch",
                subject_topics=["DSA", "System Design", "OS", "DBMS"],
                join_code="CSA2026",
                student_count=0
            )
            session.add(test_class)
            await session.flush()

        # Create 3 Mock Students under this class
        mock_students_data = [
            ("student1@example.com", "Rohan", "Sharma", 42.0, "low"),
            ("student2@example.com", "Aditya", "Verma", 68.5, "neutral"),
            ("student3@example.com", "Priya", "Patel", 89.0, "high")
        ]
        
        for email, f_name, l_name, prs, mood in mock_students_data:
            s_stmt = select(User).where(User.email == email)
            student = (await session.execute(s_stmt)).scalars().first()
            if not student:
                student = User(
                    email=email,
                    password_hash=get_password_hash("password"),
                    role_id=role_map["User"],
                    is_active=True,
                    is_email_verified=True
                )
                session.add(student)
                await session.flush()
                
                # Profile
                s_prof = Profile(
                    user_id=student.id,
                    first_name=f_name,
                    last_name=l_name,
                    phone="910000000" + str(uuid.uuid4().int)[:2],
                    target_role="Software Developer",
                    target_company_type="Product",
                    education_tier="tier3",
                    placement_readiness_score=prs
                )
                session.add(s_prof)

                # StudentProfile
                s_sp = StudentProfile(
                    user_id=student.id,
                    college_name="State Engineering College",
                    graduation_year=2026,
                    degree="B.Tech",
                    branch="Computer Science",
                    cgpa=7.5,
                    onboarding_step=3,
                    placement_readiness_score=prs,
                    acquisition_channel="whatsapp_organic"
                )
                session.add(s_sp)
                
                # Link to class
                link = FacultyClassStudent(
                    class_id=test_class.id,
                    student_id=student.id,
                    pending_email=email,
                    status="linked",
                    linked_at=datetime.utcnow()
                )
                session.add(link)
                test_class.student_count += 1

                # Add a mock completed session to calculate metrics
                sess = InterviewSession(
                    user_id=student.id,
                    session_mode="practice",
                    target_role="Software Developer",
                    difficulty_level=5.0,
                    status="completed",
                    started_at=datetime.utcnow() - timedelta(days=2),
                    ended_at=datetime.utcnow() - timedelta(days=2) + timedelta(minutes=20),
                    confidence_score=75.0
                )
                session.add(sess)
                await session.flush()

                score = InterviewScore(
                    session_id=sess.id,
                    technical_correctness=float(prs),
                    communication_clarity=float(prs + 5),
                    confidence_tone=70.0,
                    completeness=float(prs - 5),
                    feedback_summary="Strong foundation but need to work on boundary cases."
                )
                session.add(score)

        # 7. Seed Vernacular Analogies
        concept_stmt = select(VernacularConcept).limit(1)
        existing_concept = (await session.execute(concept_stmt)).scalars().first()
        if not existing_concept:
            concepts = [
                VernacularConcept(
                    language="Hindi",
                    concept_key="recursion",
                    concept_name="Recursion",
                    translation="पुनरावृत्ति (Recursion)",
                    local_analogy="दादी की कहानी के अंदर एक और कहानी - जब तक कि मुख्य पात्र सो न जाए।",
                    explanation="एक फ़ंक्शन जो खुद को तब तक कॉल करता रहता है जब तक कि वह बेस कंडीशन (अंत) तक न पहुँच जाए।"
                ),
                VernacularConcept(
                    language="Hindi",
                    concept_key="stack",
                    concept_name="Stack",
                    translation="ढेर (Stack)",
                    local_analogy="शादी की प्लेटों का ढेर - जो प्लेट सबसे बाद में रखी गई है, उसे सबसे पहले उठाया जाता है (LIFO)।",
                    explanation="एक रैखिक डेटा संरचना जो 'लास्ट इन फर्स्ट आउट' (LIFO) सिद्धांत का पालन करती है।"
                ),
                VernacularConcept(
                    language="Telugu",
                    concept_key="queue",
                    concept_name="Queue",
                    translation="వరుస క్రమం (Queue)",
                    local_analogy="సినిమా టికెట్ క్యూ లైన్ - మొదట వచ్చిన వారికి మొదట టికెట్ లభిస్తుంది (FIFO).",
                    explanation="ఒక డేటా స్ట్రక్చర్, ఇది 'ఫస్ట్ ఇన్ ఫస్ట్ అవుట్' (FIFO) సూత్రాన్ని అనుసరిస్తుంది."
                )
            ]
            session.add_all(concepts)

        # 8. Seed Offline Bundles
        bundle_stmt = select(OfflineBundle).limit(1)
        existing_bundle = (await session.execute(bundle_stmt)).scalars().first()
        if not existing_bundle:
            bundles = [
                OfflineBundle(
                    role_category="software_engineer",
                    version=1,
                    s3_key="bundles/software_engineer_v1.json",
                    question_count=3,
                    file_size_bytes=1024,
                    generated_at=datetime.utcnow()
                ),
                OfflineBundle(
                    role_category="product_manager",
                    version=1,
                    s3_key="bundles/product_manager_v1.json",
                    question_count=3,
                    file_size_bytes=1200,
                    generated_at=datetime.utcnow()
                )
            ]
            session.add_all(bundles)

        await session.commit()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_resilience_demo())
