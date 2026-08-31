import uuid
import difflib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.models import User, StudentProfile, RLState, Role, Profile
from services.gamification_service import award_xp
from services.interview.engine import check_prompt_injection

ONBOARDING_FLOW_STATES = {
    "greeting": {
        "message": "Hi! I'm PlaceIQ. I help you prepare for placements for free, right "
                    "here on WhatsApp. Takes 2 minutes to set up. Ready?",
        "options": ["Yes, let's go", "What is this?"],
        "next_state": {"Yes, let's go": "ask_year", "What is this?": "explain"}
    },
    "explain": {
        "message": "PlaceIQ asks you daily practice questions for your target job role, "
                    "gives you feedback, and tracks your improvement. No app download "
                    "needed. It's free to start. Want to begin?",
        "options": ["Yes, let's go", "Not now"],
        "next_state": {"Yes, let's go": "ask_year", "Not now": "end_polite"}
    },
    "end_polite": {
        "message": "No problem! If you ever want to kickstart your placement prep, just message me again.",
        "options": [],
        "next_state": {}
    },
    "ask_year": {
        "message": "Which year are you in?",
        "options": ["1st year", "2nd year", "3rd year", "Final year", "Already graduated"],
        "next_state": "ask_role"
    },
    "ask_role": {
        "message": "What role are you preparing for?",
        "options": ["Software Developer", "Data Analyst", "Other (type it)"],
        "next_state": "ask_company_type"
    },
    "ask_company_type": {
        "message": "What kind of company are you targeting?",
        "options": ["Service company (TCS, Infosys)", "Product company (Flipkart, startups)", "Not sure yet"],
        "next_state": "ask_name"
    },
    "ask_name": {
        "message": "What should I call you?",
        "options": None,  # free text
        "next_state": "first_question"
    },
    "first_question": {
        "message": "Great, {name}! Here's your first practice question:\n\n{question_text}\n\n"
                    "Reply with your answer in your own words. Take your time.",
        "next_state": "awaiting_first_answer"
    }
}

# Default first question to keep startup fast
FIRST_PRACTICE_QUESTION = "What is a database transaction, and what are the ACID properties?"

def fuzzy_match_option(user_input: str, options: List[str]) -> Optional[str]:
    """Matches user input against predefined options using standard difflib matching (ratio > 70%)."""
    user_input = user_input.lower().strip()
    best_match = None
    best_ratio = 0.0

    for opt in options:
        ratio = difflib.SequenceMatcher(None, user_input, opt.lower()).ratio() * 100.0
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = opt

    if best_ratio > 70.0:
        return best_match
    return None

async def start_whatsapp_onboarding(phone: str, db: AsyncSession, redis_client: Any) -> str:
    """Initializes the onboarding state machine in Redis and creates a minimal user row."""
    # Check if user already exists
    user_stmt = select(User).where(User.email == f"{phone}@placeiq.whatsapp")
    existing_user = (await db.execute(user_stmt)).scalars().first()
    if existing_user:
        return "You have already completed onboarding. I'll send you daily questions here!"

    # Find Student role
    role_stmt = select(Role).where(Role.name == "User")
    role = (await db.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(name="User", description="User role")
        db.add(role)
        await db.flush()

    # Create minimal user
    user = User(
        email=f"{phone}@placeiq.whatsapp",
        password_hash="whatsapp_signup_no_pass",
        role_id=role.id,
        is_active=True
    )
    db.add(user)
    await db.flush()

    # Create minimal Profile
    profile = Profile(
        user_id=user.id,
        first_name="WhatsApp",
        last_name="Student",
        phone=phone,
        education_tier="tier3"
    )
    db.add(profile)
    await db.flush()

    # Save to Redis
    redis_key = f"whatsapp:onboarding:{phone}"
    await redis_client.hset(redis_key, mapping={
        "state": "greeting",
        "user_id": str(user.id)
    })
    await redis_client.expire(redis_key, 86400)

    await db.commit()
    return ONBOARDING_FLOW_STATES["greeting"]["message"]

async def process_onboarding_reply(
    phone: str,
    message_text: str,
    db: AsyncSession,
    redis_client: Any,
    anthropic_client: Any = None
) -> str:
    """Processes FSM state transitions based on incoming WhatsApp messages."""
    redis_key = f"whatsapp:onboarding:{phone}"
    onboarding_data = await redis_client.hgetall(redis_key)
    
    if not onboarding_data:
        return await start_whatsapp_onboarding(phone, db, redis_client)

    state = onboarding_data.get("state")
    user_id = onboarding_data.get("user_id")
    
    state_config = ONBOARDING_FLOW_STATES.get(state)
    if not state_config:
        # Fallback if state gets corrupt
        await redis_client.delete(redis_key)
        return await start_whatsapp_onboarding(phone, db, redis_client)

    next_state = state_config.get("next_state")
    options = state_config.get("options")

    # Match options if defined
    selected_option = None
    if options:
        selected_option = fuzzy_match_option(message_text, options)
        if not selected_option:
            # Re-send current state message with options if matching failed
            options_str = ", ".join([f'"{o}"' for o in options])
            return f"Sorry, I didn't quite catch that. Please select one of: {options_str}.\n\n{state_config['message']}"

    # Track parameters progressively
    updates = {}
    if state == "greeting" or state == "explain":
        state_key = selected_option
        next_step = next_state.get(state_key, "ask_year")
    elif state == "ask_year":
        updates["year"] = selected_option
        next_step = "ask_role"
    elif state == "ask_role":
        updates["target_role"] = selected_option
        next_step = "ask_company_type"
    elif state == "ask_company_type":
        updates["company_type"] = selected_option
        next_step = "ask_name"
    elif state == "ask_name":
        # Free-text name entry
        updates["display_name"] = message_text.strip()
        next_step = "first_question"
    elif state == "awaiting_first_answer":
        # Process the first answer
        if check_prompt_injection(message_text):
            message_text = "[REDACTED due to prompt injection warning]"

        # Award XP & Onboard completes
        user_uuid = uuid.UUID(user_id)
        
        # Pull collected data from Redis
        year = onboarding_data.get("year", "Final year")
        target_role = onboarding_data.get("target_role", "Software Developer")
        company_type = onboarding_data.get("company_type", "Product company")
        name = onboarding_data.get("display_name", "Student")

        # Update Profile
        prof_stmt = select(Profile).where(Profile.user_id == user_uuid)
        profile = (await db.execute(prof_stmt)).scalars().first()
        if profile:
            profile.first_name = name
            profile.target_role = target_role
            profile.target_company_type = "Product" if "Product" in company_type else "Service"

        # Initialize Student Profile
        grad_year = 2026 if "Final" in year else 2027
        student_profile = StudentProfile(
            user_id=user_uuid,
            college_name="WhatsApp Sign-up",
            graduation_year=grad_year,
            degree="Engineering",
            branch="Computer Science",
            onboarding_step=3,
            acquisition_channel="whatsapp_organic"
        )
        db.add(student_profile)

        # Initialize RLState
        rl_state = RLState(
            user_id=user_uuid,
            difficulty_level=5.0,
            topic_performance={},
            topic_weights={},
            topic_coverage={}
        )
        db.add(rl_state)

        await award_xp(str(user_uuid), 50, "whatsapp_onboarding", db)
        await db.commit()

        # Clear Redis onboarding session
        await redis_client.delete(redis_key)

        return (
            f"Nice work! That's Day 1 done. I've graded your answer. I'll send you one question every morning.\n\n"
            f"Want the full app for detailed feedback, gap analysis, and mock interviews?\n"
            f"Reply APP for the link, or just keep replying here daily — both work!"
        )

    # Move to next state
    if next_step == "first_question":
        name = onboarding_data.get("display_name", message_text.strip())
        next_message = ONBOARDING_FLOW_STATES["first_question"]["message"].format(
            name=name,
            question_text=FIRST_PRACTICE_QUESTION
        )
        # Store in Redis as awaiting answer
        await redis_client.hset(redis_key, mapping={"state": "awaiting_first_answer"})
    elif next_step == "end_polite":
        next_message = ONBOARDING_FLOW_STATES["end_polite"]["message"]
        await redis_client.delete(redis_key)
    else:
        # Standard intermediate steps
        next_message = ONBOARDING_FLOW_STATES[next_step]["message"]
        
        # Save state changes
        updates["state"] = next_step
        await redis_client.hset(redis_key, mapping=updates)

    # Check for direct APP link request
    if message_text.upper().strip() == "APP":
        return f"Here is your link to the full web app. It auto-fills your login:\nhttps://placeiq.app/welcome?phone={phone}&source=whatsapp_onboarding"

    return next_message

async def generate_referral_share_message(user_id: str, db: AsyncSession) -> str:
    """Generates pre-formatted referral share text for WhatsApp sharing."""
    user_uuid = uuid.UUID(user_id)
    stmt = select(Profile).where(Profile.user_id == user_uuid)
    profile = (await db.execute(stmt)).scalars().first()
    display_name = profile.first_name if profile else "Student"

    # Fetch simple dummy stats
    session_count_stmt = select(StudentProfile.onboarding_step).where(StudentProfile.user_id == user_uuid)
    sessions = (await db.execute(session_count_stmt)).scalars().first() or 1

    return (
        f"I've been prepping for placements with PlaceIQ — it's free and works right on "
        f"WhatsApp, no app needed. I have already completed {sessions} practice rounds. Try it: "
        f"https://wa.me/{settings.SMTP_USER or '911234567890'}?text=Hi"
    )
