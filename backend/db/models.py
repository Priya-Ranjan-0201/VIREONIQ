import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Text, Integer, Numeric, ForeignKey, DateTime, Float, SmallInteger, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from db.session import Base

# ==========================================
# IDENTITY & ACCESS
# ==========================================

class Role(Base):
    __tablename__ = 'roles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255))
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False, index=True)
    is_email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    role = relationship("Role", back_populates="users")
    profile = relationship("Profile", back_populates="user", uselist=False)
    recruiter = relationship("Recruiter", back_populates="user", uselist=False)

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = Column(String(1024), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    device_id = Column(String(255))
    ip_address = Column(INET)
    user_agent = Column(Text)
    last_active_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OtpCode(Base):
    __tablename__ = 'otp_codes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    contact = Column(String(255), nullable=False)
    code = Column(String(10), nullable=False)
    purpose = Column(String(50), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = Column(String(100), nullable=False)
    entity = Column(String(50))
    entity_id = Column(UUID(as_uuid=True))
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ==========================================
# USER PERSONAS
# ==========================================

class Profile(Base):
    __tablename__ = 'profiles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    target_role = Column(String(100), index=True)
    target_company_type = Column(String(50))
    education_tier = Column(String(20))
    placement_readiness_score = Column(Numeric(5, 2), default=0.00)
    allow_recruiter_discovery = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")

class Company(Base):
    __tablename__ = 'companies'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    company_type = Column(String(50))
    website = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    recruiters = relationship("Recruiter", back_populates="company")

class Recruiter(Base):
    __tablename__ = 'recruiters'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='RESTRICT'), nullable=False)
    job_title = Column(String(150))
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="recruiter")
    company = relationship("Company", back_populates="recruiters")

# ==========================================
# PREPARATION & EVALUATION CORE
# ==========================================

class Resume(Base):
    __tablename__ = 'resumes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    storage_key = Column(String(512), unique=True, nullable=False)
    mime_type = Column(String(100), nullable=False)
    parsed_data = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))
    
    scores = relationship("ResumeScore", back_populates="resume", cascade="all, delete-orphan")

class ResumeScore(Base):
    __tablename__ = 'resume_scores'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False)
    overall_score = Column(Numeric(5, 2), nullable=False)
    keyword_match_score = Column(Numeric(5, 2))
    completeness_score = Column(Numeric(5, 2))
    quantified_achievements_score = Column(Numeric(5, 2))
    action_verb_score = Column(Numeric(5, 2))
    formatting_score = Column(Numeric(5, 2))
    role_relevance_score = Column(Numeric(5, 2))
    improvement_notes = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="scores")

class Skill(Base):
    __tablename__ = 'skills'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), unique=True, nullable=False)
    category = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ResumeEntity(Base):
    __tablename__ = 'resume_entities'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False)
    entity_type = Column(String(50), nullable=False) # 'technology', 'action_verb', 'quantified_achievement'
    entity_value = Column(String(255), nullable=False)
    context = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", backref="entities")

class TargetRole(Base):
    __tablename__ = 'target_roles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(String(150), unique=True, nullable=False)
    required_skills = Column(JSONB) # List of required technical skills
    min_projects = Column(Integer, default=2)
    min_experience_years = Column(Numeric(3, 1), default=0.0)
    salary_band_base = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class GapAnalysis(Base):
    __tablename__ = 'gap_analysis'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    target_role_id = Column(UUID(as_uuid=True), ForeignKey('target_roles.id'), nullable=True)
    target_role_name = Column(String(100), nullable=False)
    company_type = Column(String(50))
    
    # Dimension Scores (0-100)
    technical_gap_score = Column(Numeric(5, 2))
    communication_gap_score = Column(Numeric(5, 2))
    project_gap_score = Column(Numeric(5, 2))
    confidence_gap_score = Column(Numeric(5, 2))
    consistency_gap_score = Column(Numeric(5, 2))
    overall_readiness_score = Column(Numeric(5, 2))
    
    # Dimension Severities ('Critical', 'Moderate', 'Minor', 'None')
    technical_gap_severity = Column(String(20))
    communication_gap_severity = Column(String(20))
    project_gap_severity = Column(String(20))
    confidence_gap_severity = Column(String(20))
    consistency_gap_severity = Column(String(20))
    
    missing_skills = Column(JSONB) # List of strings
    placement_probability = Column(Numeric(5, 2)) # Percentage
    expected_salary_band = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    recommendations = relationship("GapRecommendation", backref="gap_analysis", cascade="all, delete-orphan")

class GapRecommendation(Base):
    __tablename__ = 'gap_recommendations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gap_analysis_id = Column(UUID(as_uuid=True), ForeignKey('gap_analysis.id', ondelete='CASCADE'), nullable=False)
    time_horizon_days = Column(Integer, nullable=False) # 30, 60, or 90
    dimension = Column(String(50)) # 'technical', 'communication', etc
    task_description = Column(Text, nullable=False)
    resources = Column(JSONB) # Links or study materials
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ==========================================
# INTERVIEW ENGINE
# ==========================================

class InterviewSession(Base):
    __tablename__ = 'interview_sessions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    session_mode = Column(String(50), nullable=False)
    target_role = Column(String(100))
    difficulty_level = Column(Numeric(4, 2), default=1.00)
    status = Column(String(20), default='in_progress', index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    confidence_score = Column(Numeric(5, 2))
    transcript = Column(JSONB, default=list)
    annotations = Column(JSONB, default=list)

    score_breakdown = relationship("InterviewScore", back_populates="session", uselist=False, cascade="all, delete-orphan")
    answers = relationship("InterviewAnswer", back_populates="session", cascade="all, delete-orphan")

    @property
    def technical_score(self):
        if self.score_breakdown and self.score_breakdown.technical_correctness is not None:
            return float(self.score_breakdown.technical_correctness)
        return None

    @property
    def overall_score(self):
        if self.score_breakdown and self.score_breakdown.technical_correctness is not None:
            return float(self.score_breakdown.technical_correctness)
        return None

# --- Recommendation & Outcomes Engine ---

class JobListing(Base):
    __tablename__ = "job_listings"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    company_tier = Column(String) # Product, Startup, Service
    description = Column(Text)
    required_skills = Column(Text) # Stored as comma-separated
    location = Column(String)
    salary_min = Column(Float)
    salary_max = Column(Float)
    is_remote = Column(Boolean, default=False)
    job_type = Column(String)
    source_url = Column(String)
    source = Column(String, default="Internal") # LinkedIn, Naukri, Internal
    posted_at = Column(DateTime, default=datetime.utcnow)
    competition_index = Column(Float, default=0.5) # 0.0 (Low) to 1.0 (High)
    language_support = Column(String, default="English") # English, Hindi, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    target_roles = Column(Text) # Comma-separated
    preferred_locations = Column(Text) # Comma-separated
    min_salary_target = Column(Float)
    remote_only = Column(Boolean, default=False)
    experience_level = Column(String)
    
    user = relationship("User", backref=backref("preferences", uselist=False))

class JobMatch(Base):
    __tablename__ = "job_matches"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    job_id = Column(String, ForeignKey("job_listings.id"))
    match_score = Column(Float) # Legacy aggregate
    skill_fit_score = Column(Float)
    offer_probability_score = Column(Float)
    confidence_level = Column(String) # Low, Medium, High
    explanation_json = Column(JSONB) # { "reasons": [], "missing": [] }
    ai_feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="matches")
    job = relationship("JobListing")

class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    job_id = Column(String, ForeignKey("job_listings.id"))
    interaction_type = Column(String) # impression, click, save, apply, dismiss
    created_at = Column(DateTime, default=datetime.utcnow)

class MarketSignal(Base):
    __tablename__ = "market_signals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(String, index=True)
    skill_name = Column(String(150), unique=True, index=True) # Specific skill trend
    source = Column(String(50)) # 'GitHub', 'LinkedIn', 'JD_Scraper'
    demand_level = Column(String) # High, Moderate, Low
    demand_velocity = Column(Float) # Trend direction
    relevance_score = Column(Float)
    avg_salary = Column(Float)
    trending_skills = Column(JSONB)
    metadata_json = Column(JSONB) # Raw ingested data
    last_updated = Column(DateTime, default=datetime.utcnow)
    captured_at = Column(DateTime(timezone=True), server_default=func.now())

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    job_id = Column(String, ForeignKey("job_listings.id"))
    status = Column(String, default="saved") # saved, applied, oa, interview, final, offer, rejected
    stage_id = Column(Integer, default=1) # Numeric representation for sorting
    is_referral = Column(Boolean, default=False)
    notes = Column(Text)
    rejection_reason = Column(String)
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", backref=backref("applications", cascade="all, delete-orphan"))
    job = relationship("JobListing")
    events = relationship("ApplicationEvent", backref="application", cascade="all, delete-orphan")
    offer = relationship("Offer", back_populates="application", uselist=False, cascade="all, delete-orphan")

class ApplicationEvent(Base):
    __tablename__ = "application_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(String, ForeignKey("applications.id"))
    event_type = Column(String) # Interview Scheduled, OA Received, Follow-up Sent
    event_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Offer(Base):
    __tablename__ = "offers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(String, ForeignKey("applications.id"), unique=True)
    base_salary = Column(Float)
    currency = Column(String, default="INR")
    bonus = Column(Float)
    equity_text = Column(String)
    location = Column(String)
    deadline = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    application = relationship("Application", back_populates="offer")

# --- Payments & Monetization ---

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    plan_id = Column(String, default="free") # free, lite, growth, premium
    status = Column(String, default="active") # active, expired, canceled
    razorpay_subscription_id = Column(String, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref=backref("subscription", uselist=False))

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    amount = Column(Float)
    currency = Column(String, default="INR")
    razorpay_order_id = Column(String)
    razorpay_payment_id = Column(String, nullable=True)
    status = Column(String, default="pending") # pending, success, failed
    created_at = Column(DateTime, default=datetime.utcnow)

# --- Analytics & Beta Launch ---

class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    event_type = Column(String) # signup, upload, search, upgrade_click
    metadata_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Waitlist(Base):
    __tablename__ = "waitlist"
    
    email = Column(String, primary_key=True)
    full_name = Column(String)
    referred_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class InterviewScore(Base):
    __tablename__ = 'interview_scores'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('interview_sessions.id', ondelete='CASCADE'), unique=True, nullable=False)
    technical_correctness = Column(Numeric(5, 2))
    communication_clarity = Column(Numeric(5, 2))
    confidence_tone = Column(Numeric(5, 2))
    completeness = Column(Numeric(5, 2))
    feedback_summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("InterviewSession", back_populates="score_breakdown")

class InterviewAnswer(Base):
    __tablename__ = 'interview_answers'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('interview_sessions.id', ondelete='CASCADE'), nullable=False)
    turn_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text)
    answer_audio_url = Column(String(512))
    response_latency_ms = Column(Integer)
    hedging_word_count = Column(Integer)
    ai_evaluation = Column(JSONB)
    reward_signal = Column(Numeric(5, 2))
    cognitive_load_score = Column(Numeric(4, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("InterviewSession", back_populates="answers")

class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    application_id = Column(String, ForeignKey("applications.id"), nullable=True)
    title = Column(String)
    message = Column(Text)
    remind_at = Column(DateTime)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ExternalCalendar(Base):
    __tablename__ = "external_calendars"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    provider = Column(String) # google, outlook
    access_token = Column(Text)
    refresh_token = Column(Text)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ==========================================
# RECRUITER & MARKET INTELLIGENCE
# ==========================================

class RecruiterPersona(Base):
    __tablename__ = 'recruiter_personas'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False) # e.g., 'Skeptical Tech Lead', 'FAANG Senior EM'
    company_context = Column(String(50)) # 'Startup', 'FAANG', 'Product', 'Service'
    personality_traits = Column(JSONB) # { "skepticism": 0.8, "speed": 0.9, "empathy": 0.2 }
    focus_areas = Column(JSONB) # ["Architecture", "Edge Cases", "Scalability"]
    communication_style = Column(String(50)) # 'Direct', 'Inquisitive', 'Pressure-based'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class HiringRubric(Base):
    __tablename__ = 'hiring_rubrics'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=True)
    role_category = Column(String(100), nullable=False)
    evaluation_criteria = Column(JSONB) # { "GCA": 0.4, "RoleRelatedKnowledge": 0.6 }
    passing_threshold = Column(Numeric(4, 2), default=0.70)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# ==========================================
# COGNITIVE & MULTI-AGENT EVALUATION
# ==========================================

class CognitiveProfile(Base):
    __tablename__ = 'cognitive_profiles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    # Intelligence Dimensions
    debugging_ability = Column(Numeric(5, 2), default=0.0)
    architecture_thinking = Column(Numeric(5, 2), default=0.0)
    ownership_mindset = Column(Numeric(5, 2), default=0.0)
    communication_under_pressure = Column(Numeric(5, 2), default=0.0)
    dna_vector = Column(JSONB) # 128-Dimensional Psychometric Vector
    dominant_archetype = Column(String(100)) # 'System Architect', 'Rapid Prototyper', etc.
    
    history_json = Column(JSONB) # Historical trend of these scores
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class CareerPath(Base):
    __tablename__ = 'career_paths'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    current_role_goal = Column(String(100))
    suggested_pivot = Column(String(100)) # If GPS suggests rerouting
    reroute_reason = Column(Text)
    
    milestones = Column(JSONB) # [{ "title": "Master Redis", "status": "pending" }]
    market_synchronicity_score = Column(Numeric(5, 2), default=0.0) # How aligned with market?
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class AgentEvaluation(Base):
    __tablename__ = 'agent_evaluations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('interview_sessions.id', ondelete='CASCADE'), nullable=False)
    agent_type = Column(String(50), nullable=False) # 'Technical', 'Behavioral', 'BarRaiser'
    score = Column(Numeric(5, 2))
    reasoning_log = Column(Text) # The "Why" behind the score
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    type = Column(String(50), nullable=False) # INTERVIEW, OFFER, SYSTEM, NUDGE
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    action_url = Column(String(512))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ==========================================
# USER AUTH SESSION
# ==========================================

class UserAuthSession(Base):
    """Detailed authentication session with device fingerprint and revocation reason."""
    __tablename__ = 'user_auth_sessions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    device_fingerprint = Column(Text)
    ip_address = Column(INET)
    user_agent = Column(Text)
    is_revoked = Column(Boolean, default=False)
    revocation_reason = Column(String(255))
    last_active_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', backref=backref('auth_sessions', cascade='all, delete-orphan'))


# ==========================================
# STUDENT PROFILE EXTENDED
# ==========================================

class StudentProfile(Base):
    """Detailed student-specific profile with academic and placement data."""
    __tablename__ = 'student_profiles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    college_name = Column(String(255))
    graduation_year = Column(SmallInteger)
    degree = Column(String(100))
    branch = Column(String(100))
    cgpa = Column(Numeric(4, 2))
    city = Column(String(100))
    state = Column(String(100))
    years_of_experience = Column(Numeric(3, 1), default=0.0)
    linkedin_url = Column(String(512))
    github_url = Column(String(512))
    portfolio_url = Column(String(512))
    onboarding_step = Column(SmallInteger, default=0)
    placement_readiness_score = Column(Numeric(5, 2), default=0.00)
    acquisition_channel = Column(String(50), nullable=True)  # whatsapp_organic | whatsapp_referral | etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', backref=backref('student_profile', uselist=False))

    @property
    def institution_tier(self) -> str:
        if self.user and getattr(self.user, 'profile', None):
            return self.user.profile.education_tier or "tier3"
        return "tier3"


# ==========================================
# COLLEGE & PARENT B2B
# ==========================================

class CollegeProfile(Base):
    """B2B college admin profile for institutional placement tracking."""
    __tablename__ = 'college_profiles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    college_name = Column(String(255), nullable=False)
    affiliation = Column(String(255))
    state = Column(String(100))
    tier = Column(String(20), default='tier_3')  # tier_1, tier_2, tier_3
    naac_grade = Column(String(5))
    total_students = Column(Integer)
    placement_officer_name = Column(String(150))
    contact_email = Column(String(255))
    subscription_plan = Column(String(50), default='free')
    subscription_expiry = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', backref=backref('college_profile', uselist=False))


class ParentProfile(Base):
    """Read-only parent dashboard profile linked to a student user."""
    __tablename__ = 'parent_profiles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    student_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    relation = Column(String(50), default='parent')  # parent, guardian
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', foreign_keys=[user_id], backref=backref('parent_profile', uselist=False))
    student = relationship('User', foreign_keys=[student_user_id])


# ==========================================
# REINFORCEMENT LEARNING
# ==========================================

class RLState(Base):
    """Reinforcement learning adaptive state for each student, persisted across sessions."""
    __tablename__ = 'rl_states'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    difficulty_level = Column(Numeric(4, 2), default=3.00)  # 1.00 - 10.00
    topic_performance = Column(JSONB, default=dict)  # {"DSA": 0.72, "System Design": 0.43}
    topic_weights = Column(JSONB, default=dict)       # {"DSA": 1.5, "OS": 2.0}
    topic_coverage = Column(JSONB, default=dict)      # {"DSA": 5, "System Design": 2}
    last_topic_tested = Column(JSONB, default=dict)   # {"DSA": "2024-01-01T10:00:00"}
    reward_history = Column(JSONB, default=list)      # Last 20 reward signals
    total_sessions = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    avg_time_per_answer_s = Column(Numeric(8, 2), default=0.0)
    confidence_estimate = Column(Numeric(4, 3), default=0.500)
    avoided_topics = Column(JSONB, default=list)
    strong_topics = Column(JSONB, default=list)
    weak_topics = Column(JSONB, default=list)
    optimal_session_length = Column(Integer, default=10)  # Questions per session
    last_session_id = Column(UUID(as_uuid=True), ForeignKey('interview_sessions.id'), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', backref=backref('rl_state', uselist=False))


# ==========================================
# SKILL DECAY (EBBINGHAUS)
# ==========================================

class SkillDecayModel(Base):
    """Ebbinghaus forgetting curve state per student per topic."""
    __tablename__ = 'skill_decay_models'
    __table_args__ = (UniqueConstraint('user_id', 'topic_name', name='uq_skill_decay_user_topic'),)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    topic_name = Column(String(150), nullable=False, index=True)
    mastery_level = Column(Numeric(4, 3), default=0.000)   # 0.0 - 1.0
    last_tested_at = Column(DateTime(timezone=True), nullable=True)
    last_score = Column(Numeric(5, 2), nullable=True)
    stability_days = Column(Numeric(6, 2), default=7.00)   # Ebbinghaus stability constant
    predicted_retention = Column(Numeric(4, 3), default=1.000)  # Current retention estimate
    alert_threshold = Column(Numeric(4, 3), default=0.700)  # Alert when retention < this
    last_alert_sent_at = Column(DateTime(timezone=True), nullable=True)
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', backref='skill_decay_models')


# ==========================================
# PSYCHOMETRIC DNA
# ==========================================

class PsychometricProfile(Base):
    """Multi-session behavioral fingerprint and 128-dim DNA placement vector."""
    __tablename__ = 'psychometric_profiles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    response_latency_by_topic = Column(JSONB, default=dict)   # {"DSA": 45.2, "OS": 90.1} (seconds)
    avoidance_counts = Column(JSONB, default=dict)             # {"System Design": 3}
    confidence_collapse_triggers = Column(JSONB, default=list) # ["concurrency", "graphs"]
    recovery_rate = Column(Numeric(4, 3), default=0.500)       # 0.0 - 1.0
    risk_appetite_score = Column(Numeric(4, 3), default=0.500)
    persistence_score = Column(Numeric(4, 3), default=0.500)
    dna_vector = Column(JSONB, default=list)  # 128-dimensional float array
    dna_version = Column(Integer, default=0)
    dna_computed_at = Column(DateTime(timezone=True), nullable=True)
    hire_prob_service = Column(Numeric(5, 2), default=0.00)
    hire_prob_product = Column(Numeric(5, 2), default=0.00)
    hire_prob_startup = Column(Numeric(5, 2), default=0.00)
    hire_prob_faang = Column(Numeric(5, 2), default=0.00)
    sessions_required = Column(Integer, default=3)
    sessions_completed = Column(Integer, default=0)
    profile_type_label = Column(String(100))  # e.g., 'The Methodical Architect'
    placement_probability_history = Column(JSONB, default=list) # [{"date": "2024-01-01", "probability": 85.5}]
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', backref=backref('psychometric_profile', uselist=False))


# ==========================================
# COGNITIVE LOAD EVENTS
# ==========================================

class CognitiveLoadEvent(Base):
    """Logs instances of detected cognitive overload during interview sessions."""
    __tablename__ = 'cognitive_load_events'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('interview_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    question_number = Column(Integer, nullable=False)
    load_score = Column(Numeric(4, 3), nullable=False)  # 0.0 - 1.0
    contributing_signals = Column(JSONB)  # {"long_pause_ms": 12000, "backspace_rate": 0.4}
    action_taken = Column(String(100))    # 'difficulty_reduced', 'hint_offered', 'break_suggested'
    difficulty_before = Column(Numeric(4, 2))
    difficulty_after = Column(Numeric(4, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ==========================================
# GAMIFICATION
# ==========================================

class GamificationProfile(Base):
    """XP, levels, streaks, badges and leaderboard ranks per student."""
    __tablename__ = 'gamification_profiles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    total_xp = Column(Integer, default=0)
    weekly_xp = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    current_streak_days = Column(Integer, default=0)
    longest_streak_days = Column(Integer, default=0)
    last_activity_date = Column(DateTime(timezone=True), nullable=True)
    streak_freeze_count = Column(Integer, default=0)
    earned_badges = Column(JSONB, default=list)  # [{"badge_id": "first_interview", "earned_at": "..."}]
    rank_global = Column(Integer, nullable=True)
    rank_role = Column(Integer, nullable=True)
    rank_institution = Column(Integer, nullable=True)
    rank_weekly = Column(Integer, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', backref=backref('gamification', uselist=False))


class BadgeReference(Base):
    """Catalog of all available badges with unlock conditions."""
    __tablename__ = 'badge_references'
    badge_id = Column(String(50), primary_key=True)  # e.g., 'first_interview'
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    unlock_condition = Column(Text)  # Human-readable condition description
    category = Column(String(50))  # 'milestone', 'streak', 'performance', 'social'
    icon_name = Column(String(50))  # Lucide icon name
    xp_reward = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ==========================================
# PREPARATION CALENDAR
# ==========================================

class PreparationCalendar(Base):
    """AI-generated 30/60/90-day study plans with daily task breakdowns."""
    __tablename__ = 'preparation_calendars'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    gap_analysis_id = Column(UUID(as_uuid=True), ForeignKey('gap_analysis.id'), nullable=True)
    plan_type = Column(Integer, nullable=False)  # 30, 60, or 90
    start_date = Column(DateTime(timezone=True), nullable=False)
    daily_tasks = Column(JSONB, nullable=False)   # [{"day": 1, "date": "...", "topic": "...", "tasks": [...]}]
    completion_map = Column(JSONB, default=dict)  # {"day_1": true, "day_2": false}
    ics_key = Column(String(255), unique=True)    # UUID key for .ics download URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', backref='preparation_calendars')


# ==========================================
# MARKET INTELLIGENCE & BENCHMARKS
# ==========================================

class MarketIntelligence(Base):
    """Weekly job market signals — trending/declining skills, salary data."""
    __tablename__ = 'market_intelligence'
    __table_args__ = (UniqueConstraint('role_category', 'week_start_date', name='uq_market_role_week'),)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_category = Column(String(100), nullable=False, index=True)
    week_start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    trending_skills = Column(JSONB)   # [{"skill": "LangChain", "demand_score": 87}]
    declining_skills = Column(JSONB)
    new_requirements = Column(JSONB)
    saturation_signals = Column(JSONB)
    top_certifications = Column(JSONB)
    salary_signals = Column(JSONB)    # {"p50": 1800000, "p75": 2400000}
    jd_count_analyzed = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PeerBenchmark(Base):
    """Anonymized percentile score distributions by role, company type, and institution tier."""
    __tablename__ = 'peer_benchmarks'
    __table_args__ = (UniqueConstraint('role_id', 'company_type', 'institution_tier', name='uq_benchmark_role_company_tier'),)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey('target_roles.id'), nullable=False, index=True)
    company_type = Column(String(50), nullable=False)
    institution_tier = Column(String(20), nullable=False)
    ats_percentiles = Column(JSONB)           # [45, 58, 70, 82, 91]
    overall_percentiles = Column(JSONB)
    technical_percentiles = Column(JSONB)
    communication_percentiles = Column(JSONB)
    skill_gap_percentiles = Column(JSONB)
    sample_size = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ==========================================
# REVERSE INTERVIEW SESSIONS
# ==========================================

class ReverseInterviewSession(Base):
    """Sessions where the student practices asking the interviewer strategic questions."""
    __tablename__ = 'reverse_interview_sessions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_session_id = Column(UUID(as_uuid=True), ForeignKey('interview_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    questions_asked = Column(JSONB, default=list)  # Student's questions
    ai_reactions = Column(JSONB, default=list)     # AI hiring manager reactions
    strategic_thinking_score = Column(Numeric(5, 2))
    role_understanding_score = Column(Numeric(5, 2))
    culture_fit_score = Column(Numeric(5, 2))
    business_acumen_score = Column(Numeric(5, 2))
    overall_score = Column(Numeric(5, 2))
    text_feedback = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', backref='reverse_interview_sessions')


# ==========================================
# OFFER LETTERS
# ==========================================

class OfferLetter(Base):
    """Mock offer/rejection letters generated after completing the full interview pipeline."""
    __tablename__ = 'offer_letters'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    letter_type = Column(String(20), nullable=False)   # 'offer', 'rejection', 'development_plan'
    readiness_score_at_generation = Column(Numeric(5, 2))
    simulated_company = Column(String(150))
    simulated_role = Column(String(150))
    ctc_offered_thousands = Column(Numeric(10, 2))     # For offer letters
    letter_content = Column(JSONB, nullable=False)     # Structured letter JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', backref='offer_letters')


# ==========================================
# COMPANY INTERVIEW PROFILES
# ==========================================

class CompanyInterviewProfile(Base):
    """Stores company-specific interview structure, question weights, and LP mappings."""
    __tablename__ = 'company_interview_profiles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_key = Column(String(50), unique=True, nullable=False, index=True)  # 'google', 'amazon', 'tcs'
    display_name = Column(String(100), nullable=False)
    company_type = Column(String(50), nullable=False)  # 'FAANG', 'Product', 'Service', 'Startup'
    interview_stages = Column(JSONB)    # Ordered list of stage names
    question_style_weights = Column(JSONB)  # {"DSA": 0.5, "Behavioral": 0.3, "System Design": 0.2}
    evaluation_criteria = Column(JSONB)
    leadership_principles = Column(JSONB)   # Amazon LPs — null for others
    difficulty_level = Column(String(20))   # 'Medium', 'Hard', 'Expert'
    estimated_ctc_min_lpa = Column(Numeric(6, 2))
    estimated_ctc_max_lpa = Column(Numeric(6, 2))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ==========================================
# MISSING BASE MODELS
# ==========================================

class RealInterviewDebrief(Base):
    """Anonymous verified interview experience reports."""
    __tablename__ = 'real_interview_debriefs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    company_name = Column(String(200), nullable=False, index=True)
    role = Column(String(200), nullable=False, index=True)
    interview_date = Column(DateTime(timezone=True), nullable=False)
    round_type = Column(String(50), nullable=False) # e.g., 'technical_round_1'
    difficulty = Column(String(20)) # 'easy', 'medium', 'hard', 'very_hard'
    outcome = Column(String(30), nullable=False) # 'passed', 'failed', 'pending'
    topics_tested = Column(JSONB, nullable=False) # e.g., ['arrays', 'binary tree']
    specific_questions = Column(JSONB) # List of strings or QA structures
    what_worked = Column(Text)
    what_did_not_work = Column(Text)
    would_change = Column(Text)
    is_anonymous = Column(Boolean, default=True, nullable=False)
    xp_reward_given = Column(Boolean, default=False, nullable=False)
    is_quality_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', backref='debriefs')

class NetworkConnection(Base):
    """Alumni and mentor network contacts for referral outreach."""
    __tablename__ = 'network_connections'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    target_company = Column(String(200), nullable=False, index=True)
    target_role = Column(String(200))
    path_type = Column(String(30), nullable=False) # 'alumni_direct', etc
    connection_name = Column(String(300), nullable=False)
    connection_linkedin_url = Column(String(512))
    connection_company = Column(String(200), nullable=False)
    connection_role = Column(String(200), nullable=False)
    connection_college = Column(String(200))
    warmth_score = Column(Integer, nullable=False) # 1 - 10
    reachability_score = Column(Integer, nullable=False) # 1 - 10
    recommended_approach = Column(Text, nullable=False)
    generated_outreach_message = Column(Text)
    outreach_message_scores = Column(JSONB) # e.g. {"clarity": 8}
    status = Column(String(30), default='not_contacted', nullable=False)
    last_interaction_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    is_opted_in_consent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', backref='network_connections')

class OutreachMessage(Base):
    """Outreach message history and iteration telemetry."""
    __tablename__ = 'outreach_messages'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    connection_id = Column(UUID(as_uuid=True), ForeignKey('network_connections.id', ondelete='SET NULL'))
    message_type = Column(String(30), nullable=False) # 'linkedin_connection', etc
    draft_text = Column(Text, nullable=False)
    specificity_score = Column(Integer)
    reciprocity_score = Column(Integer)
    action_clarity_score = Column(Integer)
    length_score = Column(Integer)
    response_ease_score = Column(Integer)
    response_probability_estimate = Column(Numeric(4, 2))
    issues_detected = Column(JSONB)
    improved_version = Column(Text)
    iteration_number = Column(Integer, default=1, nullable=False)
    was_sent = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime(timezone=True))
    response_received = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', backref='outreach_messages')
    connection = relationship('NetworkConnection', backref='messages')

class DayOfInterviewPlan(Base):
    """Personalized checklist and warmup protocol for the day of an interview."""
    __tablename__ = 'day_of_interview_plans'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    target_company = Column(String(200), nullable=False)
    target_role = Column(String(200), nullable=False)
    interview_datetime = Column(DateTime(timezone=True), nullable=False)
    plan_generated_at = Column(DateTime(timezone=True), server_default=func.now())
    phase_1_warmup = Column(JSONB, nullable=False) # Warmup tasks
    phase_2_transition = Column(JSONB, nullable=False)
    phase_3_launch = Column(JSONB, nullable=False)
    reminder_sent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', backref='day_of_interview_plans')

class ResumeABTest(Base):
    """Resume A/B testing analytics and score comparisons."""
    __tablename__ = 'resume_ab_tests'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    target_role = Column(String(200), nullable=False)
    target_company = Column(String(200))
    resume_a_id = Column(UUID(as_uuid=True), ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False)
    resume_b_id = Column(UUID(as_uuid=True), ForeignKey('resumes.id', ondelete='CASCADE'))
    ats_score_a = Column(Numeric(5, 2))
    ats_score_b = Column(Numeric(5, 2))
    signal_score_a = Column(Numeric(5, 2))
    signal_score_b = Column(Numeric(5, 2))
    winner = Column(String(1)) # 'A' or 'B'
    difference_analysis = Column(JSONB)
    recommendation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', backref='resume_ab_tests')


# ==========================================
# SESSION 22 — INVISIBLE DEGREE
# ==========================================

class SkillCredential(Base):
    """Tamper-proof, verifiable student skill credential."""
    __tablename__ = 'skill_credentials'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    tier = Column(String(20), nullable=False) # e.g. 'gold'
    overall_prs = Column(Numeric(5, 2), nullable=False)
    sessions_completed = Column(Integer, nullable=False)
    technical_depth = Column(Numeric(5, 2))
    communication_clarity = Column(Numeric(5, 2))
    problem_solving = Column(Numeric(5, 2))
    consistency_under_pressure = Column(Numeric(5, 2))
    learning_velocity = Column(Numeric(5, 2))
    code_quality = Column(Numeric(5, 2))
    system_thinking = Column(Numeric(5, 2))
    domain_expertise = Column(Numeric(5, 2))
    recruiter_summary = Column(Text)
    credential_hash = Column(String(64), unique=True, nullable=False, index=True)
    public_url = Column(String(300), nullable=False)
    issued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)

    user = relationship('User', backref=backref('credential', uselist=False))


# ==========================================
# SESSION 23 — CAREER REBIRTH
# ==========================================

class CareerRebirthPlan(Base):
    """AI Transition roadmaps and transferable skill reframings for switchers."""
    __tablename__ = 'career_rebirth_plans'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    current_domain = Column(String(100))
    target_role = Column(String(100))
    career_break_reason = Column(String(100))
    break_duration_months = Column(Integer)
    available_hours_per_week = Column(Numeric(4, 1))
    weeks_to_completion = Column(Integer)
    completion_target_date = Column(DateTime(timezone=True))
    phases = Column(JSONB, nullable=False)
    transferable_skills = Column(JSONB)
    break_nullifier_strategy = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', backref='career_rebirth_plans')


# ==========================================
# SESSION 24 — COMMUNICATION UPLIFT
# ==========================================

class LanguageProgression(Base):
    """Code-switch telemetry and bridge progression mapping."""
    __tablename__ = 'language_progressions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    primary_language = Column(String(10), default='en', nullable=False)
    current_bridge_phase = Column(Integer, default=1, nullable=False)
    sessions_in_native = Column(Integer, default=0, nullable=False)
    sessions_in_english = Column(Integer, default=0, nullable=False)
    avg_technical_score_native = Column(Numeric(5, 2))
    avg_technical_score_english = Column(Numeric(5, 2))
    vocabulary_mastered = Column(JSONB, default=list, nullable=False)
    bridge_started_at = Column(DateTime(timezone=True), server_default=func.now())
    phase_upgrade_dates = Column(JSONB, default=list, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship('User', backref=backref('language_progression', uselist=False))


# ==========================================
# SESSION 26 — 1000 MENTORS
# ==========================================

class MentorProfile(Base):
    """Verified placed students give-back mentoring commitments."""
    __tablename__ = 'mentor_profiles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    placement_company = Column(String(200))
    placement_role = Column(String(200))
    placement_ctc = Column(Integer)
    college_name = Column(String(300))
    company_type = Column(String(30))
    commitment_start_date = Column(DateTime(timezone=True), server_default=func.now())
    commitment_end_date = Column(DateTime(timezone=True))
    sessions_committed = Column(Integer, default=12, nullable=False)
    sessions_completed = Column(Integer, default=0, nullable=False)
    mentees_active = Column(JSONB, default=list, nullable=False) # List of UUIDs
    avg_mentee_rating = Column(Numeric(3, 2))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', backref=backref('mentor_profile', uselist=False))

class MentorSession(Base):
    """Mentoring session calendar bookings and ratings."""
    __tablename__ = 'mentor_sessions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey('mentor_profiles.id', ondelete='CASCADE'), nullable=False, index=True)
    mentee_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    session_type = Column(String(50), nullable=False) # 'technical_mock', etc
    status = Column(String(20), default='scheduled', nullable=False) # 'scheduled', 'completed', etc
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=60, nullable=False)
    meeting_link = Column(String(300))
    agenda = Column(JSONB)
    mentor_rating = Column(Integer)
    mentee_rating = Column(Integer)
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    mentor = relationship('MentorProfile', backref='sessions')
    mentee = relationship('User', backref='mentee_sessions')


# ==========================================
# SESSION 27 — COMPANY TRUTH DATABASE
# ==========================================

class CompanyTruthAggregate(Base):
    """Aggregated interview experiences mapping process and timeline realities."""
    __tablename__ = 'company_truth_aggregates'
    __table_args__ = (UniqueConstraint('company_name', 'role_category', name='uq_truth_company_role'),)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(200), nullable=False, index=True)
    role_category = Column(String(100), nullable=False, index=True)
    submission_count = Column(Integer, default=0, nullable=False)
    quality_verified_count = Column(Integer, default=0, nullable=False)
    stage_map = Column(JSONB)
    avg_rounds = Column(Numeric(3, 1))
    surprise_stages = Column(JSONB)
    top_topics = Column(JSONB)
    verified_questions = Column(JSONB)
    timeline_reality = Column(JSONB)
    ghost_rate = Column(Numeric(5, 2))
    offer_intelligence = Column(JSONB)
    equity_score = Column(Numeric(5, 2))
    last_aggregated_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ==========================================
# SESSION 28 — REFERRAL ECONOMY
# ==========================================

class ReferralSlot(Base):
    """Quarterly referral slots linked between insiders and candidates."""
    __tablename__ = 'referral_slots'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    company_name = Column(String(200), nullable=False, index=True)
    role_name = Column(String(200), nullable=False)
    status = Column(String(30), default='matched', nullable=False) # 'matched', 'accepted', etc.
    quarter = Column(String(10), nullable=False) # e.g. "2025-Q1"
    referrer_note = Column(Text)
    matched_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True))
    submitted_at = Column(DateTime(timezone=True))
    outcome = Column(String(30)) # 'hired', 'rejected', etc.
    outcome_logged_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    referrer = relationship('User', foreign_keys=[referrer_id], backref='referrals_given')
    candidate = relationship('User', foreign_keys=[candidate_id], backref='referrals_received')


# ==========================================
# SESSION 29 — HIGH SCHOOLS
# ==========================================

class HighSchoolTrajectory(Base):
    """4-Year Career pathing roadmaps starting at age 16."""
    __tablename__ = 'highschool_trajectories'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    current_class = Column(Integer, nullable=False) # 9-12
    target_role = Column(String(100))
    interest_areas = Column(JSONB)
    hours_per_week = Column(Numeric(4, 1))
    years_to_placement = Column(Integer)
    year_plans = Column(JSONB, nullable=False)
    milestones_completed = Column(JSONB, default=dict, nullable=False)
    last_market_refresh_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', backref=backref('highschool_trajectory', uselist=False))


# ==========================================
# SESSION 30 — EMPLOYER TRUTH SCORE
# ==========================================

class EmployerTruthScore(Base):
    """Aggregate accountability scoring for candidate experience."""
    __tablename__ = 'employer_truth_scores'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(200), unique=True, nullable=False, index=True)
    overall_score = Column(Numeric(5, 2), nullable=False)
    label = Column(String(50), nullable=False) # 'Candidate First', etc.
    transparency_score = Column(Numeric(5, 2))
    timeline_score = Column(Numeric(5, 2))
    ghost_rate = Column(Numeric(5, 2))
    feedback_score = Column(Numeric(5, 2))
    equity_score = Column(Numeric(5, 2))
    submission_count = Column(Integer, default=0, nullable=False)
    prev_month_score = Column(Numeric(5, 2))
    last_computed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class EmployerFlag(Base):
    """Alerts and flag submissions reporting candidate experience issues."""
    __tablename__ = 'employer_flags'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(200), nullable=False, index=True)
    reason = Column(Text, nullable=False)
    reported_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    status = Column(String(20), default='pending', nullable=False) # 'pending', 'reviewed', etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    reporter = relationship('User', backref='employer_flags')


# ==========================================
# SESSION 31 — GLOBAL PARITY
# ==========================================

class TalentPassport(Base):
    """Cross-border talent verified credential passport."""
    __tablename__ = 'talent_passports'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    passport_id = Column(String(30), unique=True, nullable=False, index=True)
    country_code = Column(String(2), nullable=False)
    verified_role = Column(String(100))
    skill_tier = Column(String(20))
    prs_score = Column(Numeric(5, 2))
    english_proficiency_tier = Column(String(100))
    eligible_company_tiers = Column(JSONB)
    visa_pathways = Column(JSONB)
    contractor_rate_min = Column(Integer)
    contractor_rate_max = Column(Integer)
    public_passport_url = Column(String(300))
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', backref=backref('talent_passport', uselist=False))


# ==========================================
# SESSION 32 — COMMUNITY & VIRAL GROWTH
# ==========================================

class DailyChallenge(Base):
    """Daily coding/interview challenges with community-wide leaderboards."""
    __tablename__ = 'daily_challenges'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(20), nullable=False)  # easy | medium | hard
    category = Column(String(50), nullable=False)  # dsa | system_design | behavioral | sql
    challenge_date = Column(DateTime(timezone=True), nullable=False, index=True, unique=True)
    solution_template = Column(Text)
    test_cases = Column(JSONB)
    hints = Column(JSONB)
    time_limit_minutes = Column(Integer, default=30)
    xp_reward = Column(Integer, default=50)
    participants_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DailyChallengeSubmission(Base):
    """User submissions for daily challenges."""
    __tablename__ = 'daily_challenge_submissions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey('daily_challenges.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    solution_code = Column(Text)
    language = Column(String(30))
    score = Column(Integer, default=0)
    time_taken_seconds = Column(Integer)
    passed_tests = Column(Integer, default=0)
    total_tests = Column(Integer, default=0)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('challenge_id', 'user_id', name='uq_challenge_user'),
    )

    challenge = relationship('DailyChallenge', backref='submissions')
    user = relationship('User', backref='challenge_submissions')


class StudyGroup(Base):
    """Peer study groups formed by target role + timezone for collaborative prep."""
    __tablename__ = 'study_groups'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    target_role = Column(String(100), nullable=False, index=True)
    timezone = Column(String(50), nullable=False)
    language = Column(String(30), default='en')
    max_members = Column(Integer, default=6)
    current_members = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    meeting_schedule = Column(JSONB)  # { day: "Monday", time: "18:00", frequency: "weekly" }
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship('User', backref='created_study_groups')


class StudyGroupMember(Base):
    """Membership records for study groups."""
    __tablename__ = 'study_group_members'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey('study_groups.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('group_id', 'user_id', name='uq_group_user'),
    )

    group = relationship('StudyGroup', backref='members')
    user = relationship('User', backref='study_group_memberships')


class CommunityPost(Base):
    """Social achievement feed for viral sharing of milestones."""
    __tablename__ = 'community_posts'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    post_type = Column(String(30), nullable=False)  # achievement | challenge_win | streak | credential
    title = Column(String(300), nullable=False)
    content = Column(Text)
    post_metadata = Column("metadata", JSONB)  # { badge_name, score, streak_days, etc. }
    likes_count = Column(Integer, default=0)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', backref='community_posts')


# ==========================================
# SESSIONS 32 TO 41 — LAST MILE CORE MODELS
# ==========================================

class OfflineBundle(Base):
    """Pre-generated question bundles stored locally/S3 for offline interviews."""
    __tablename__ = 'offline_bundles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_category = Column(String(100), nullable=False)
    version = Column(Integer, nullable=False)
    s3_key = Column(String(500), nullable=False)
    question_count = Column(Integer, nullable=False)
    file_size_bytes = Column(Integer)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('role_category', 'version', name='uq_role_version'),
    )


class FacultyClass(Base):
    """Faculty-created student cohorts targeting specific technical syllabi."""
    __tablename__ = 'faculty_classes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    faculty_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    class_name = Column(String(200), nullable=False)
    subject_topics = Column(JSONB)
    join_code = Column(String(20), unique=True, nullable=False)
    student_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    faculty = relationship('User', backref='managed_classes')


class FacultyClassStudent(Base):
    """Mapping of students linked or pending join to a faculty class."""
    __tablename__ = 'faculty_class_students'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_id = Column(UUID(as_uuid=True), ForeignKey('faculty_classes.id', ondelete='CASCADE'), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    pending_email = Column(String(255), nullable=True)
    status = Column(String(20), default='pending')  # pending | linked | removed
    linked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('class_id', 'student_id', name='uq_class_student'),
        UniqueConstraint('class_id', 'pending_email', name='uq_class_email'),
    )

    class_ = relationship('FacultyClass', backref='student_mappings')
    student = relationship('User', backref='faculty_memberships')


class EarnToLearnLedger(Base):
    """Tracks premium days earned via community contributions."""
    __tablename__ = 'earn_to_learn_ledger'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    contribution_type = Column(String(50), nullable=False)
    reference_id = Column(UUID(as_uuid=True), nullable=True)
    premium_days = Column(Integer, nullable=False)
    status = Column(String(20), default='pending_verification')  # pending_verification | credited | rejected
    credited_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', backref='earn_ledger')


class UserPremiumStatus(Base):
    """User-specific premium tier access details."""
    __tablename__ = 'user_premium_status'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    premium_until = Column(DateTime(timezone=True), nullable=True)
    source = Column(String(20), default='earned')  # earned | paid | gifted | trial
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', backref=backref('premium_status', uselist=False))


class ContentReviewQueue(Base):
    """Queue for human-in-the-loop validation of student translations/analogies."""
    __tablename__ = 'content_review_queue'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contributor_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content_type = Column(String(50))
    content_text = Column(Text)
    target_language = Column(String(10), nullable=True)
    status = Column(String(20), default='pending')  # pending | approved | rejected
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    contributor = relationship('User', foreign_keys=[contributor_id], backref='contributions')
    reviewer = relationship('User', foreign_keys=[reviewer_id], backref='reviewed_items')


class ParentLink(Base):
    """Maintains student-consented link records to parents/guardians."""
    __tablename__ = 'parent_links'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    parent_phone = Column(String(20), nullable=False)
    parent_name = Column(String(200))
    consent_status = Column(String(20), default='pending')  # pending | active | revoked | delivery_failed
    consent_requested_at = Column(DateTime(timezone=True), server_default=func.now())
    consented_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship('User', backref='parent_connections')


class MoodCheckin(Base):
    """Tracks pre-session mood self-reporting for mental health pacing checks."""
    __tablename__ = 'mood_checkins'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    mood_value = Column(String(20), nullable=False)  # positive | neutral | low
    checked_in_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', backref='mood_checkins')


class StudyGroupSession(Base):
    """Sessions organized within study groups for mock peer interviews."""
    __tablename__ = 'study_group_sessions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey('study_groups.id', ondelete='CASCADE'), nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    interviewer_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    interviewee_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = Column(String(20), default='scheduled')  # scheduled | completed | cancelled
    meeting_link = Column(String(300))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    group = relationship('StudyGroup', backref='sessions')
    interviewer = relationship('User', foreign_keys=[interviewer_id], backref='conducted_peer_sessions')
    interviewee = relationship('User', foreign_keys=[interviewee_id], backref='taken_peer_sessions')


class PeerFeedback(Base):
    """Mock interview evaluation notes and ratings compiled by peers."""
    __tablename__ = 'peer_feedbacks'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('study_group_sessions.id', ondelete='CASCADE'), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reviewee_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    technical_rating = Column(Integer, nullable=False)
    communication_rating = Column(Integer, nullable=False)
    confidence_rating = Column(Integer, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship('StudyGroupSession', backref='feedbacks')
    reviewer = relationship('User', foreign_keys=[reviewer_id], backref='given_peer_feedbacks')
    reviewee = relationship('User', foreign_keys=[reviewee_id], backref='received_peer_feedbacks')


class VernacularConcept(Base):
    """Concept descriptions and local analogies in regional languages."""
    __tablename__ = 'vernacular_concepts'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    language = Column(String(10), nullable=False, index=True)
    concept_key = Column(String(100), nullable=False, index=True)
    concept_name = Column(String(200), nullable=False)
    translation = Column(Text, nullable=False)
    local_analogy = Column(Text)
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('language', 'concept_key', name='uq_language_concept'),
    )


# ==========================================
# VIREONIQ X: CAREER INTELLIGENCE & EVIDENCE
# ==========================================

class SkillEvidence(Base):
    """
    Evidence-based skill intelligence tracking the 5-tier evidence hierarchy:
    CLAIMED -> INFERRED -> DEMONSTRATED -> ASSESSED -> VERIFIED.
    """
    __tablename__ = 'skill_evidences'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False, index=True)
    evidence_tier = Column(String(30), default='CLAIMED', nullable=False, index=True) # CLAIMED | INFERRED | DEMONSTRATED | ASSESSED | VERIFIED
    source_type = Column(String(50), default='RESUME', nullable=False) # RESUME | GITHUB | CODING_LAB | INTERVIEW | CREDENTIAL | PROJECT
    score = Column(Numeric(5, 2), default=0.00, nullable=False) # 0-100
    confidence = Column(String(20), default='MEDIUM', nullable=False) # HIGH | MEDIUM | LOW
    evidence_count = Column(Integer, default=1)
    evidence_details = Column(JSONB, default=list) # List of specific evidence items, artifacts, test runs
    last_verified_at = Column(DateTime(timezone=True), server_default=func.now())
    freshness_score = Column(Numeric(5, 2), default=100.00) # Decay score 0-100 based on age
    explanation = Column(Text) # Transparent human-readable reasoning
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref=backref("skill_evidences", cascade="all, delete-orphan"))


class ProjectEvidence(Base):
    """
    Normalized project capability evidence linked to GitHub repositories and live deployments.
    """
    __tablename__ = 'project_evidences'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    repo_url = Column(String(512))
    live_url = Column(String(512))
    technologies = Column(JSONB, default=list)
    complexity_score = Column(Numeric(5, 2), default=50.00) # 0-100 based on architecture depth
    demonstrated_competencies = Column(JSONB, default=list) # Skills practically evidenced
    verification_status = Column(String(30), default='UNVERIFIED') # UNVERIFIED | INFERRED | VERIFIED
    evidence_metrics = Column(JSONB, default=dict) # Commits, PRs, architecture patterns
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref=backref("project_evidences", cascade="all, delete-orphan"))


class AssessmentResult(Base):
    """
    Controlled coding lab assessments, Big-O static AST analysis, and test run telemetry.
    """
    __tablename__ = 'assessment_results'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    assessment_type = Column(String(50), nullable=False) # CODING_LAB | BIG_O | SYSTEM_DESIGN | ALGORITHMS
    problem_title = Column(String(255), nullable=False)
    language = Column(String(50), nullable=False)
    code_submitted = Column(Text, nullable=False)
    passed_test_cases = Column(Integer, default=0)
    total_test_cases = Column(Integer, default=0)
    runtime_ms = Column(Float, default=0.0)
    memory_kb = Column(Float, default=0.0)
    time_complexity_static = Column(String(50)) # e.g. O(N log N) from AST
    time_complexity_empirical = Column(String(50)) # from test curve
    space_complexity = Column(String(50))
    quality_score = Column(Numeric(5, 2), default=0.00) # 0-100
    integrity_score = Column(Numeric(5, 2), default=95.00) # 0-100
    integrity_signals = Column(JSONB, default=dict) # paste_burst, timing_anomaly, similarity
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref=backref("assessment_results", cascade="all, delete-orphan"))


class InterviewRubricEvaluation(Base):
    """
    Multi-dimensional structured rubric evaluations across DSA, System Design, and Behavioral domains.
    """
    __tablename__ = 'interview_rubric_evaluations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('interview_sessions.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role_target = Column(String(100), nullable=False)
    dimension_scores = Column(JSONB, default=dict) # {decomposition, complexity, scalability, tradeoffs}
    communication_indicators = Column(JSONB, default=dict) # Observable proxies: speech_rate, pauses, hedging
    strengths = Column(JSONB, default=list)
    weaknesses = Column(JSONB, default=list)
    next_recommended_actions = Column(JSONB, default=list)
    overall_interview_score = Column(Numeric(5, 2), nullable=False)
    evaluator_confidence = Column(String(20), default='HIGH')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("InterviewSession", backref=backref("rubric_evaluation", uselist=False))
    user = relationship("User", backref=backref("interview_rubric_evaluations", cascade="all, delete-orphan"))


class CareerReadinessScore(Base):
    """
    Multi-dimensional Career Readiness Index (CRI) historical snapshots with transparent rationale.
    """
    __tablename__ = 'career_readiness_scores'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    target_role = Column(String(100), nullable=False, index=True)
    overall_readiness = Column(Numeric(5, 2), nullable=False) # 0-100
    technical_capability = Column(Numeric(5, 2), default=0.0)
    project_capability = Column(Numeric(5, 2), default=0.0)
    coding_mastery = Column(Numeric(5, 2), default=0.0)
    system_design = Column(Numeric(5, 2), default=0.0)
    communication_score = Column(Numeric(5, 2), default=0.0)
    interview_readiness = Column(Numeric(5, 2), default=0.0)
    resume_evidence_strength = Column(Numeric(5, 2), default=0.0)
    role_alignment = Column(Numeric(5, 2), default=0.0)
    dimension_explanations = Column(JSONB, default=dict) # {dimension: {why, evidence, confidence, next_action}}
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref=backref("career_readiness_history", cascade="all, delete-orphan"))


class PrescriptiveIntervention(Base):
    """
    Structured 14-day / 30-day intervention pathway generated from ROI-prioritized skill gaps.
    """
    __tablename__ = 'prescriptive_interventions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    gap_skill = Column(String(100), nullable=False)
    duration_days = Column(Integer, default=14)
    priority_score = Column(Numeric(6, 2), default=0.0) # ROI prioritization score
    roi_metric = Column(JSONB, default=dict) # {importance, gap, career_impact, estimated_effort}
    milestones = Column(JSONB, default=list) # List of day-by-day roadmap objectives, projects, assessments
    status = Column(String(30), default='ACTIVE') # ACTIVE | COMPLETED | ARCHIVED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref=backref("prescriptive_interventions", cascade="all, delete-orphan"))


class DailyMission(Base):
    """
    Personal Career Operating System daily missions adapting to user schedule and target role.
    """
    __tablename__ = 'daily_missions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    mission_date = Column(String(10), nullable=False, index=True) # YYYY-MM-DD
    tasks = Column(JSONB, default=list) # [{id, title, category, estimated_minutes, projected_readiness_delta, completed, action_url}]
    total_estimated_minutes = Column(Integer, default=60)
    total_projected_delta = Column(Numeric(4, 2), default=0.5)
    completion_rate = Column(Numeric(5, 2), default=0.0)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref=backref("daily_missions", cascade="all, delete-orphan"))


class CounterfactualSimulationLog(Base):
    """
    Records "What-If" scenarios and projected readiness score trajectories with confidence intervals.
    """
    __tablename__ = 'counterfactual_simulations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    scenario_type = Column(String(100), nullable=False)
    input_parameters = Column(JSONB, default=dict)
    projected_readiness = Column(Numeric(5, 2), nullable=False)
    confidence_interval = Column(JSONB, default=dict) # {lower, upper}
    affected_skills = Column(JSONB, default=list)
    expected_gap_reduction = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref=backref("counterfactual_simulations", cascade="all, delete-orphan"))


class AIObservabilityLog(Base):
    """
    Observability telemetry logging AI model usage, latency, tokens, cost, and validation status.
    """
    __tablename__ = 'ai_observability_logs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_name = Column(String(100), nullable=False, index=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    prompt_version = Column(String(50), default='v1.0')
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    latency_ms = Column(Float, default=0.0)
    cost_estimate_usd = Column(Numeric(8, 6), default=0.0)
    validation_passed = Column(Boolean, default=True)
    fallback_triggered = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class CanonicalSkill(Base):
    """
    Canonical normalized skill entity with category, hierarchical nesting, and alias mapping.
    """
    __tablename__ = 'canonical_skills'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(100), nullable=False, index=True) # Programming | Databases | Architecture | DevOps | Cloud | AI/ML | Frontend | Security
    parent_id = Column(UUID(as_uuid=True), ForeignKey('canonical_skills.id', ondelete='SET NULL'), nullable=True)
    description = Column(Text)
    aliases = Column(JSONB, default=list) # e.g. ["python3", "python 3", "python programming"]
    proficiency_rubric = Column(JSONB, default=dict) # 1-5 level criteria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    children = relationship("CanonicalSkill", backref=backref("parent", remote_side=[id]))


class SkillRelationship(Base):
    """
    Directed semantic relationship between canonical skills (prerequisite, parent, related, complementary, alternative).
    """
    __tablename__ = 'skill_relationships'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_skill_id = Column(UUID(as_uuid=True), ForeignKey('canonical_skills.id', ondelete='CASCADE'), nullable=False, index=True)
    target_skill_id = Column(UUID(as_uuid=True), ForeignKey('canonical_skills.id', ondelete='CASCADE'), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False, index=True) # prerequisite | parent | child | related | complementary | alternative
    strength = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    source_skill = relationship("CanonicalSkill", foreign_keys=[source_skill_id])
    target_skill = relationship("CanonicalSkill", foreign_keys=[target_skill_id])


class EvidenceItem(Base):
    """
    Universal granular evidence atom supporting source provenance, lineage,
    deduplication across source groups, and freshness state tracking.
    """
    __tablename__ = 'evidence_items'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    skill_id = Column(UUID(as_uuid=True), ForeignKey('canonical_skills.id', ondelete='SET NULL'), nullable=True, index=True)
    skill_name = Column(String(100), nullable=False, index=True)
    evidence_type = Column(String(50), nullable=False, index=True) # RESUME_CLAIM | PROJECT_REPO | CODING_ASSESSMENT | INTERVIEW_SESSION | CERTIFICATE | WORK_EXPERIENCE
    source = Column(String(100), nullable=False) # RESUME_PDF | GITHUB_REPO | JUDGE0_SANDBOX | AUDIO_INTERVIEW | PORTFOLIO
    source_reference = Column(String(512)) # URL, storage key, or assessment session UUID
    source_span = Column(Text) # Exact text snippet, commit hash, or section span
    canonical_evidence_id = Column(UUID(as_uuid=True), ForeignKey('evidence_items.id', ondelete='SET NULL'), nullable=True) # Root evidence for deduplication
    source_group = Column(String(100), nullable=True, index=True) # Logical grouping key for deduplication e.g. "project:fastapi-ecommerce"
    status = Column(String(30), default='CLAIMED', nullable=False, index=True) # CLAIMED | INFERRED | DEMONSTRATED | ASSESSED | VERIFIED
    confidence = Column(String(20), default='MEDIUM', nullable=False) # LOW | MEDIUM | HIGH | VERY_HIGH
    observed_at = Column(DateTime(timezone=True), default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    freshness_state = Column(String(20), default='FRESH', nullable=False) # FRESH | AGING | STALE | EXPIRED
    metadata_payload = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref=backref("granular_evidence_items", cascade="all, delete-orphan"))


class CareerGoal(Base):
    """
    User-controlled structured career aspirations and target parameters.
    """
    __tablename__ = 'career_goals'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    target_role = Column(String(100), nullable=False)
    priority = Column(Integer, default=1)
    time_horizon = Column(String(50), default='6_MONTHS') # 1_MONTH | 3_MONTHS | 6_MONTHS | 1_YEAR
    experience_level = Column(String(50), default='MID') # ENTRY | JUNIOR | MID | SENIOR | STAFF
    preferred_industries = Column(JSONB, default=list) # e.g. ["Fintech", "Healthtech", "DevTools"]
    preferred_work_mode = Column(String(50), default='HYBRID') # REMOTE | HYBRID | ONSITE
    preferred_locations = Column(JSONB, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref=backref("career_goals", cascade="all, delete-orphan"))


class CareerEvent(Base):
    """
    Append-only transactional career intelligence event audit log.
    """
    __tablename__ = 'career_events'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True) # SKILL_EVIDENCE_ADDED | ASSESSMENT_COMPLETED | PROJECT_COMPLETED | INTERVIEW_COMPLETED | CREDENTIAL_VERIFIED | CAREER_GOAL_CHANGED | TARGET_ROLE_CHANGED
    event_data = Column(JSONB, default=dict)
    actor = Column(String(50), default='USER') # USER | SYSTEM_EVALUATOR | SANDBOX_RUNNER | ASSESSOR
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", backref=backref("career_events", cascade="all, delete-orphan"))


# ==========================================
# PHASE 4: UNIFIED ASSESSMENT & MEASUREMENT DOMAIN
# ==========================================

class AssessmentBlueprint(Base):
    """
    Role-specific assessment blueprint defining competency weights, difficulty range, and duration.
    """
    __tablename__ = 'assessment_blueprints'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(String(100), nullable=False, index=True)
    version = Column(String(20), default='4.0.0', nullable=False)
    competency_weights = Column(JSONB, default=dict) # e.g. {"Python": 0.20, "System Design": 0.25, ...}
    difficulty_range = Column(JSONB, default=list) # ["INTERMEDIATE", "ADVANCED"]
    time_limit_minutes = Column(Integer, default=45)
    min_questions = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AssessmentQuestion(Base):
    """
    Standardized, rubric-backed assessment challenge or interview prompt.
    """
    __tablename__ = 'assessment_questions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    blueprint_id = Column(UUID(as_uuid=True), ForeignKey('assessment_blueprints.id', ondelete='SET NULL'), nullable=True, index=True)
    role_name = Column(String(100), nullable=False, index=True)
    competency = Column(String(100), nullable=False, index=True)
    difficulty = Column(String(30), default='INTERMEDIATE', nullable=False, index=True) # FOUNDATIONAL | BEGINNER | INTERMEDIATE | ADVANCED | EXPERT
    question_type = Column(String(50), default='CONCEPTUAL', nullable=False) # CONCEPTUAL | SYSTEM_DESIGN | BEHAVIORAL | CODING_CHALLENGE | DEBUGGING
    prompt = Column(Text, nullable=False)
    starter_code = Column(Text, nullable=True)
    rubric = Column(JSONB, default=dict) # Evaluation criteria defined BEFORE candidate response
    hidden_tests = Column(JSONB, default=list) # Hidden test cases unexposed to candidates
    version = Column(String(20), default='1.0.0')
    status = Column(String(30), default='ACTIVE') # ACTIVE | DRAFT | RETIRED
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AssessmentSession(Base):
    """
    Active or completed candidate assessment attempt session.
    """
    __tablename__ = 'assessment_sessions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    blueprint_id = Column(UUID(as_uuid=True), ForeignKey('assessment_blueprints.id', ondelete='SET NULL'), nullable=True)
    target_role = Column(String(100), nullable=False, index=True)
    mode = Column(String(30), default='ASSESSMENT', nullable=False) # ASSESSMENT (credential-eligible) | PRACTICE (coaching/hints)
    status = Column(String(30), default='IN_PROGRESS', nullable=False, index=True) # IN_PROGRESS | COMPLETED | ABANDONED
    current_difficulty = Column(Float, default=3.0) # 1.0 to 5.0
    competency_coverage = Column(JSONB, default=dict)
    integrity_status = Column(String(50), default='VERIFIED')
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", backref=backref("assessment_sessions", cascade="all, delete-orphan"))


class AssessmentResponseAttempt(Base):
    """
    Candidate response attempt for an individual question within a session.
    Preserves all historical attempts.
    """
    __tablename__ = 'assessment_response_attempts'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('assessment_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey('assessment_questions.id', ondelete='CASCADE'), nullable=False, index=True)
    attempt_number = Column(Integer, default=1)
    response_text = Column(Text, nullable=True)
    code_submission = Column(Text, nullable=True)
    execution_telemetry = Column(JSONB, default=dict) # AST Big-O, tests passed, runtime_ms, memory_kb
    evaluation_scores = Column(JSONB, default=dict)
    integrity_signals = Column(JSONB, default=dict)
    confidence = Column(String(20), default='HIGH') # LOW | MEDIUM | HIGH
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("AssessmentSession", backref=backref("responses", cascade="all, delete-orphan"))
    question = relationship("AssessmentQuestion")


class AssessmentEvaluationResult(Base):
    """
    Final synthesized evaluation result with grounded evidence generation.
    """
    __tablename__ = 'assessment_evaluation_results'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('assessment_sessions.id', ondelete='CASCADE'), unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    target_role = Column(String(100), nullable=False)
    overall_score = Column(Float, nullable=False) # 0-100
    dimension_scores = Column(JSONB, default=dict) # {"correctness": 92, "complexity": 85, "architecture": 78, ...}
    integrity_score = Column(Float, default=95.0)
    evidence_generated = Column(JSONB, default=list) # List of generated SkillEvidence / EvidenceItem payloads
    strengths = Column(JSONB, default=list)
    gaps = Column(JSONB, default=list)
    next_best_action = Column(JSONB, default=dict)
    evaluator_version = Column(String(20), default='4.0.0')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("AssessmentSession", backref=backref("evaluation_result", uselist=False, cascade="all, delete-orphan"))
    user = relationship("User")


# ==========================================
# PHASE 5: CAREER INTERVENTION ENGINE & DAILY CAREER OS
# ==========================================

class CareerInterventionPlan(Base):
    """
    Structured 14-day / 30-day intervention roadmap designed to close primary career bottlenecks.
    """
    __tablename__ = 'career_intervention_plans'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    target_role = Column(String(100), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    objective = Column(Text, nullable=False)
    primary_gap = Column(String(100), nullable=False, index=True)
    secondary_gaps = Column(JSONB, default=list) # e.g. ["Redis", "Distributed Systems"]
    strategy = Column(String(50), default='BALANCED', nullable=False) # FASTEST | BALANCED | HIGH_EVIDENCE | LOWEST_EFFORT | DEEP_MASTERY
    duration_days = Column(Integer, default=14)
    daily_time_budget_minutes = Column(Integer, default=60)
    estimated_effort_hours = Column(String(50), default="12-18h")
    expected_readiness_delta_range = Column(String(50), default="+4 to +7")
    status = Column(String(30), default='NOT_STARTED', nullable=False, index=True) # NOT_STARTED | IN_PROGRESS | PAUSED | COMPLETED | CANCELLED
    progress_pct = Column(Float, default=0.0)
    tasks_data = Column(JSONB, default=list) # Snapshot of tasks
    version = Column(String(20), default='5.0.0')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref=backref("intervention_plans", cascade="all, delete-orphan"))


class CareerInterventionTask(Base):
    """
    Individual actionable daily task within an intervention plan.
    """
    __tablename__ = 'career_intervention_tasks'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plan_id = Column(UUID(as_uuid=True), ForeignKey('career_intervention_plans.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    day_number = Column(Integer, default=1)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(String(50), default='LEARN', nullable=False) # LEARN | PRACTICE | BUILD | ASSESS | INTERVIEW | VERIFY | REASSESS
    estimated_minutes = Column(Integer, default=30)
    priority = Column(Integer, default=1)
    prerequisite_task_ids = Column(JSONB, default=list)
    expected_evidence_type = Column(String(50), default='LEARNING_ACTIVITY') # LEARNING_ACTIVITY | DEMONSTRATED | ASSESSED | VERIFIED
    completion_criteria = Column(Text, nullable=True)
    status = Column(String(30), default='NOT_STARTED', nullable=False, index=True) # NOT_STARTED | IN_PROGRESS | BLOCKED | COMPLETED | SKIPPED | EXPIRED
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    plan = relationship("CareerInterventionPlan", backref=backref("tasks", cascade="all, delete-orphan"))
    user = relationship("User")


class RecommendationFeedback(Base):
    """
    Candidate feedback on interventions and actions to improve recommendation quality over time.
    """
    __tablename__ = 'recommendation_feedback'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    intervention_id = Column(UUID(as_uuid=True), ForeignKey('career_intervention_plans.id', ondelete='SET NULL'), nullable=True)
    action_id = Column(String(100), nullable=True)
    feedback_type = Column(String(50), nullable=False) # USEFUL | TOO_DIFFICULT | TOO_EASY | ALREADY_KNOW | NOT_RELEVANT
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")


class WeeklyCareerReview(Base):
    """
    Synthesized weekly progress review with change attribution and next-week priority focus.
    """
    __tablename__ = 'weekly_career_reviews'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    week_start_date = Column(String(20), nullable=False, index=True) # YYYY-MM-DD
    target_role = Column(String(100), nullable=False)
    starting_readiness = Column(Float, nullable=False)
    ending_readiness = Column(Float, nullable=False)
    readiness_delta = Column(Float, nullable=False)
    evidence_count_added = Column(Integer, default=0)
    gaps_closed = Column(JSONB, default=list)
    remaining_constraints = Column(JSONB, default=list)
    attribution = Column(JSONB, default=dict)
    next_week_priority = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")


# ==========================================
# PHASE 6: TALENT PASSPORT & VERIFIED CREDENTIALS DOMAIN
# ==========================================

class VerifiedCredential(Base):
    """
    Authoritative, cryptographically signed professional competency credential.
    """
    __tablename__ = 'verified_credentials'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    competency = Column(String(100), nullable=False, index=True)
    level = Column(String(30), default='INTERMEDIATE', nullable=False) # FOUNDATIONAL | BEGINNER | INTERMEDIATE | ADVANCED | EXPERT
    credential_type = Column(String(50), default='VERIFIED_COMPETENCY', nullable=False) # ASSESSED_COMPETENCY | VERIFIED_COMPETENCY | PROJECT_EVIDENCE | COMPOSITE_COMPETENCY
    issuer = Column(String(100), default='VIREONIQ', nullable=False)
    evidence_summary = Column(JSONB, default=dict) # Assessment ID, score, project references, integrity indicators
    evidence_tier = Column(String(30), default='VERIFIED', nullable=False)
    freshness_score = Column(Float, default=100.0)
    freshness_state = Column(String(30), default='FRESH') # FRESH | AGING | STALE
    status = Column(String(30), default='ACTIVE', nullable=False, index=True) # DRAFT | ISSUED | ACTIVE | EXPIRING | EXPIRED | REVOKED | SUSPENDED
    public_reference = Column(String(100), unique=True, nullable=False, index=True) # e.g. VX-PY-9F31B2A4
    signature = Column(String(255), nullable=False) # Cryptographic HMAC-SHA256 signature
    version = Column(String(20), default='1.0.0')
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revocation_reason = Column(Text, nullable=True)
    revoked_by = Column(String(100), nullable=True)

    user = relationship("User", backref=backref("verified_credentials", cascade="all, delete-orphan"))


class TalentPassportShare(Base):
    """
    Candidate-authorized public or recruiter share link configuration.
    """
    __tablename__ = 'talent_passport_shares'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    share_token = Column(String(100), unique=True, nullable=False, index=True)
    target_role = Column(String(100), default='Backend Engineer')
    is_active = Column(Boolean, default=True, index=True)
    visible_competencies = Column(JSONB, default=list)
    visible_projects = Column(JSONB, default=list)
    visible_assessments = Column(JSONB, default=list)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    view_count = Column(Integer, default=0)

    user = relationship("User", backref=backref("passport_shares", cascade="all, delete-orphan"))


class CredentialAuditLog(Base):
    """
    Immutable audit trail recording all credential lifecycle events.
    """
    __tablename__ = 'credential_audit_logs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    credential_id = Column(UUID(as_uuid=True), ForeignKey('verified_credentials.id', ondelete='CASCADE'), nullable=False, index=True)
    action = Column(String(50), nullable=False) # ISSUED | VERIFIED | SHARED | VIEWED | SUSPENDED | REVOKED | REINSTATED
    actor = Column(String(100), default='SYSTEM')
    reason = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    credential = relationship("VerifiedCredential", backref=backref("audit_logs", cascade="all, delete-orphan"))


# ==========================================
# PHASE 7: RECRUITER INTELLIGENCE & MATCHING DOMAIN
# ==========================================

class RecruiterOrganization(Base):
    """
    Multi-tenant organization boundary for enterprise recruiters.
    """
    __tablename__ = 'recruiter_organizations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    domain = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RecruiterProfile(Base):
    """
    Recruiter user membership and role within an organization.
    """
    __tablename__ = 'recruiter_profiles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('recruiter_organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(String(50), default='RECRUITER') # RECRUITER | HIRING_MANAGER | RECRUITER_ADMIN | ORGANIZATION_ADMIN
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    organization = relationship("RecruiterOrganization", backref=backref("members", cascade="all, delete-orphan"))


class JobPosting(Base):
    """
    Structured job requirement profile for intelligent candidate matching.
    """
    __tablename__ = 'job_postings'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('recruiter_organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    target_role = Column(String(100), default='Backend Engineer', index=True)
    description = Column(Text, nullable=False)
    structured_requirements = Column(JSONB, default=dict) # {"required_skills": [{"name": "Python", "importance": 95, "min_level": "ADVANCED"}], "preferred_skills": []}
    hard_requirements = Column(JSONB, default=list) # ["Professional License", "Region Authorization"]
    status = Column(String(30), default='PUBLISHED', index=True) # DRAFT | PUBLISHED | CLOSED
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("RecruiterOrganization", backref=backref("jobs", cascade="all, delete-orphan"))


class RecruiterCandidateMatch(Base):
    """
    Multi-dimensional evidence-weighted match result with machine-readable explanations.
    """
    __tablename__ = 'recruiter_candidate_matches'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey('job_postings.id', ondelete='CASCADE'), nullable=False, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    match_score = Column(Float, nullable=False)
    match_confidence = Column(String(30), default='HIGH') # HIGH | MEDIUM | LOW
    match_quality = Column(String(50), default='GOOD_MATCH') # HIGH_CONFIDENCE_MATCH | GOOD_MATCH | PARTIAL_MATCH | INSUFFICIENT_EVIDENCE | HARD_REQUIREMENT_NOT_MET
    breakdown = Column(JSONB, default=dict) # required_skills_score, verified_evidence_score, project_score, experience_score, freshness_score
    explanation = Column(JSONB, default=dict) # strengths, partials, unknowns, main_limitation, reason_codes
    version = Column(String(20), default='7.0.0')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("JobPosting")
    candidate = relationship("User")


class RecruiterShortlist(Base):
    """
    Organization-private hiring pipeline stage and notes.
    """
    __tablename__ = 'recruiter_shortlists'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('recruiter_organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey('job_postings.id', ondelete='CASCADE'), nullable=False, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    stage = Column(String(50), default='SHORTLISTED') # DISCOVERED | SHORTLISTED | CONTACTED | ASSESSMENT | INTERVIEW | FINAL | HIRED | REJECTED
    notes = Column(JSONB, default=list) # [{"note_id": "...", "author": "...", "text": "...", "created_at": "..."}]
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("RecruiterOrganization")
    job = relationship("JobPosting")
    candidate = relationship("User")


class RecruiterSavedSearch(Base):
    """
    Saved candidate discovery searches scoped to recruiter organization.
    """
    __tablename__ = 'recruiter_saved_searches'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('recruiter_organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    query = Column(String(255), nullable=True)
    filters = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("RecruiterOrganization")


# ==========================================
# PHASE 8: EMPLOYER INTELLIGENCE & WORKFORCE CAPABILITY
# ==========================================

class OrganizationUnit(Base):
    """
    Hierarchical organizational structure (Business Unit -> Department -> Team).
    """
    __tablename__ = 'organization_units'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('recruiter_organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('organization_units.id', ondelete='CASCADE'), nullable=True)
    name = Column(String(255), nullable=False)
    unit_type = Column(String(50), default='TEAM') # BUSINESS_UNIT | DEPARTMENT | TEAM
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("RecruiterOrganization", backref=backref("units", cascade="all, delete-orphan"))
    parent = relationship("OrganizationUnit", remote_side=[id], backref=backref("sub_units", cascade="all, delete-orphan"))


class OrganizationEmployee(Base):
    """
    Authorized workforce employee profile mapped to organization units and verified skill evidence.
    """
    __tablename__ = 'organization_employees'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('recruiter_organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    unit_id = Column(UUID(as_uuid=True), ForeignKey('organization_units.id', ondelete='SET NULL'), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    role_title = Column(String(100), default='Software Engineer')
    experience_years = Column(Float, default=2.0)
    consent_level = Column(String(50), default='FULL') # FULL | ANONYMIZED | BASIC
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("RecruiterOrganization")
    unit = relationship("OrganizationUnit", backref=backref("employees", cascade="all, delete-orphan"))
    user = relationship("User")


class OrganizationRoleCatalog(Base):
    """
    Versioned organizational role definitions and competency blueprints.
    """
    __tablename__ = 'organization_role_catalogs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('recruiter_organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    level = Column(String(50), default='MID') # JUNIOR | MID | SENIOR | STAFF | PRINCIPAL | LEAD
    role_version = Column(String(20), default='1.0.0')
    required_competencies = Column(JSONB, default=list) # [{"name": "Python", "importance": 90, "min_level": "ADVANCED"}]
    preferred_competencies = Column(JSONB, default=list)
    criticality = Column(Integer, default=80) # 1 - 100
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("RecruiterOrganization")


class OrganizationCapabilitySnapshot(Base):
    """
    Immutable historical snapshot of team and organization-wide capability coverage.
    """
    __tablename__ = 'organization_capability_snapshots'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('recruiter_organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    unit_id = Column(UUID(as_uuid=True), ForeignKey('organization_units.id', ondelete='CASCADE'), nullable=True, index=True)
    snapshot_version = Column(String(20), default='8.0.0')
    overall_coverage_pct = Column(Float, nullable=False)
    confidence = Column(String(30), default='HIGH') # HIGH | MEDIUM | LOW
    matrix = Column(JSONB, default=dict) # Competency x Team matrix
    critical_gaps = Column(JSONB, default=list)
    concentration_risks = Column(JSONB, default=list)
    attribution_events = Column(JSONB, default=list) # [{"event": "EMPLOYEE_JOINED", "description": "..."}]
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("RecruiterOrganization")
    unit = relationship("OrganizationUnit")


class OrganizationAssessmentCampaign(Base):
    """
    Team and department-wide capability assessment campaign.
    """
    __tablename__ = 'organization_assessment_campaigns'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('recruiter_organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    unit_id = Column(UUID(as_uuid=True), ForeignKey('organization_units.id', ondelete='SET NULL'), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    competency = Column(String(100), nullable=False)
    target_role = Column(String(100), default='Backend Engineer')
    status = Column(String(30), default='ACTIVE') # ACTIVE | COMPLETED | ARCHIVED
    invited_count = Column(Integer, default=0)
    completed_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("RecruiterOrganization")
    unit = relationship("OrganizationUnit")


class OrganizationWorkforceIntervention(Base):
    """
    Organizational action plan (Hire, Upskill, Redeploy, Assess).
    """
    __tablename__ = 'organization_workforce_interventions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('recruiter_organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    strategy = Column(String(50), default='UPSKILL') # HIRE | UPSKILL | HYBRID | REDEPLOY | ASSESS
    target_competency = Column(String(100), nullable=False)
    tasks = Column(JSONB, default=list)
    status = Column(String(30), default='PROPOSED') # PROPOSED | IN_PROGRESS | COMPLETED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organization = relationship("RecruiterOrganization")


# ==========================================
# PHASE 9: CAREER SIMULATION & COUNTERFACTUAL PLANNING
# ==========================================

class CareerSimulation(Base):
    """
    Isolated counterfactual career scenario record with projected readiness and sensitivity analysis.
    """
    __tablename__ = 'career_simulations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    target_role = Column(String(100), default='Backend Engineer')
    simulation_type = Column(String(50), default='COMBINATION') # ROLE_SWITCH | SKILL_INVESTMENT | PROJECT_INVESTMENT | ASSESSMENT_IMPROVEMENT | TIME_INVESTMENT | COMBINATION
    base_twin_version = Column(String(20), default='2.0.0')
    assumptions = Column(JSONB, default=dict) # {"time_budget_daily_min": 60, "duration_days": 90, ...}
    hypothetical_evidence = Column(JSONB, default=list) # [{skill_name, tier: "SIMULATED", score: 85, status: "NOT_VERIFIED"}]
    projected_skills = Column(JSONB, default=dict)
    projected_readiness = Column(JSONB, default=dict) # {current, projected_min, projected_max, confidence, best_case, base_case, conservative_case}
    projected_gaps = Column(JSONB, default=dict) # {closed, reduced, remaining, transferable_skills}
    sensitivity_analysis = Column(JSONB, default=dict) # {critical_assumptions, low_impact_assumptions}
    is_private = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref=backref("career_simulations", cascade="all, delete-orphan"))


# ==========================================
# PHASE 10: AI ORCHESTRATION & EVALUATION INFRASTRUCTURE
# ==========================================

class AIOrchestrationLog(Base):
    """
    Structured observability log for all AI orchestrator invocations, tool traces, and cost metrics.
    """
    __tablename__ = 'ai_orchestration_logs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    task_type = Column(String(100), nullable=False, index=True) # RESUME_ANALYSIS | READINESS_EXPLANATION | COPILOT_CHAT | etc.
    model_name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False) # GEMINI | OPENAI | CLAUDE | LOCAL | DETERMINISTIC_FALLBACK
    prompt_version = Column(String(50), default='v1.0.0')
    latency_ms = Column(Float, default=0.0)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    estimated_cost_usd = Column(Float, default=0.0)
    tool_calls = Column(JSONB, default=list) # [{tool_name, authorized: true, latency_ms, status}]
    fallback_used = Column(Boolean, default=False)
    status = Column(String(30), default='SUCCESS') # SUCCESS | VALIDATION_FAILED | TOOL_DENIED | ERROR
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")


class AIEvaluationRun(Base):
    """
    Benchmark run record evaluating AI models on Golden Test Datasets.
    """
    __tablename__ = 'ai_evaluation_runs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_name = Column(String(100), nullable=False) # GOLDEN_READINESS_V1 | GOLDEN_RECRUITER_MATCH_V1 | etc.
    task_type = Column(String(100), nullable=False)
    model_name = Column(String(100), nullable=False)
    total_cases = Column(Integer, default=0)
    passed_cases = Column(Integer, default=0)
    groundedness_score = Column(Float, default=0.0) # 0.0 - 100.0%
    schema_validity_score = Column(Float, default=0.0) # 0.0 - 100.0%
    tool_correctness_score = Column(Float, default=0.0) # 0.0 - 100.0%
    hallucination_rate = Column(Float, default=0.0) # 0.0 - 100.0%
    details = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ==========================================
# PHASE 11: ENTERPRISE SECURITY, PRIVACY & FAIRNESS
# ==========================================

class SecurityAuditLog(Base):
    """
    Immutable audit record for Zero-Trust security events, access violations, and incident response.
    """
    __tablename__ = 'security_audit_logs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True) # TENANT_ACCESS_VIOLATION | UNAUTHORIZED_ACCESS | PROMPT_INJECTION | etc.
    severity = Column(String(30), default='MEDIUM') # LOW | MEDIUM | HIGH | CRITICAL
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(255), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    ip_address = Column(String(50), nullable=True)
    details = Column(JSONB, default=dict)
    status = Column(String(30), default='DETECTED') # DETECTED | INVESTIGATING | CONTAINED | REMEDIATED | CLOSED
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    actor = relationship("User")


class CandidatePrivacyPreference(Base):
    """
    Candidate privacy, discovery consent, and export/deletion preferences.
    """
    __tablename__ = 'candidate_privacy_preferences'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    allow_recruiter_discovery = Column(Boolean, default=True)
    allow_public_passport = Column(Boolean, default=True)
    allow_assessment_sharing = Column(Boolean, default=False)
    allow_demographic_auditing = Column(Boolean, default=True)
    consent_version = Column(String(20), default='v1.0.0')
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref=backref("privacy_preference", uselist=False, cascade="all, delete-orphan"))


class FairnessAuditReport(Base):
    """
    Demographic parity and proxy bias audit report for hiring and recommendation models.
    """
    __tablename__ = 'fairness_audit_reports'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(100), nullable=False)
    dataset_name = Column(String(100), nullable=False)
    demographic_parity_score = Column(Float, default=100.0) # 0 - 100%
    disparate_impact_ratio = Column(Float, default=1.0) # 0.8 - 1.25 is compliant
    proxy_variables_detected = Column(JSONB, default=list)
    details = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ==========================================
# PHASE 12: OUTCOME INTELLIGENCE & PRODUCT OBSERVABILITY
# ==========================================

class AnalyticsEvent(Base):
    """
    Canonical versioned analytics event record for career value funnel and platform intelligence.
    """
    __tablename__ = 'analytics_events'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(100), nullable=False, index=True) # USER_SIGNED_UP | CAREER_TWIN_CREATED | etc.
    schema_version = Column(String(20), default='v1.0.0')
    actor_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    resource_id = Column(String(255), nullable=True)
    source = Column(String(50), default='WEB_APP') # WEB_APP | API | WORKER | AI_FABRIC
    idempotency_key = Column(String(255), nullable=True, unique=True, index=True)
    metadata_ = Column('metadata', JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class CareerMilestoneProgression(Base):
    """
    Longitudinal career milestone progress tracking initial baseline vs current verified readiness.
    """
    __tablename__ = 'career_milestone_progressions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    target_role = Column(String(100), nullable=False)
    baseline_readiness = Column(Float, default=0.0)
    current_readiness = Column(Float, default=0.0)
    readiness_delta = Column(Float, default=0.0)
    verified_competencies_count = Column(Integer, default=0)
    evidence_tier_breakdown = Column(JSONB, default=dict) # {CLAIMED: X, DEMONSTRATED: Y, ASSESSED: Z, VERIFIED: W}
    current_funnel_stage = Column(String(50), default='TWIN_CREATED') # TWIN_CREATED | ASSESSED | INTERVENTION_ACTIVE | PASSPORT_READY | HIRED
    milestones_achieved = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class InterventionExperiment(Base):
    """
    Controlled A/B testing and experimentation record for career interventions.
    """
    __tablename__ = 'intervention_experiments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    hypothesis = Column(Text, nullable=False)
    variants = Column(JSONB, default=dict) # {"CONTROL": {...}, "VARIANT_A": {...}}
    primary_metric = Column(String(100), default='readiness_improvement_rate')
    guardrail_metrics = Column(JSONB, default=list) # ["dropout_rate", "assessment_failure_rate"]
    sample_size = Column(Integer, default=0)
    status = Column(String(30), default='ACTIVE') # ACTIVE | COMPLETED | STOPPED
    results = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HiringOutcomeRecord(Base):
    """
    Closed-loop outcome record tracking candidate match -> shortlist -> interview -> hire.
    """
    __tablename__ = 'hiring_outcome_records'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey('job_postings.id', ondelete='CASCADE'), nullable=False, index=True)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('recruiter_organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    match_score = Column(Float, default=0.0)
    stage = Column(String(50), default='SHORTLISTED') # SHORTLISTED | INTERVIEWED | OFFER_EXTENDED | HIRED | REJECTED
    hired_at = Column(DateTime(timezone=True), nullable=True)
    time_to_hire_days = Column(Integer, nullable=True)
    details = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ==========================================
# PHASE 13: GLOBAL SCALE, MULTI-TENANCY & DEVELOPER ECOSYSTEM
# ==========================================

class PlatformApiKey(Base):
    """
    Scoped API key for partner integrations, developer platforms, and enterprise SDK access.
    """
    __tablename__ = 'platform_api_keys'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('recruiter_organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    key_prefix = Column(String(20), nullable=False, index=True) # e.g. "vrq_live_"
    hashed_secret = Column(String(255), nullable=False)
    scopes = Column(JSONB, default=list) # ["candidate:read", "jobs:read", "assessments:read", "credentials:verify"]
    rate_limit_per_minute = Column(Integer, default=120)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WebhookSubscription(Base):
    """
    Partner event subscription for real-time career intelligence and outcome dispatch.
    """
    __tablename__ = 'webhook_subscriptions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('recruiter_organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    target_url = Column(String(500), nullable=False)
    secret_token = Column(String(255), nullable=False) # HMAC secret
    subscribed_events = Column(JSONB, default=list) # ["candidate.created", "assessment.completed", "credential.verified"]
    status = Column(String(30), default='ACTIVE') # ACTIVE | PAUSED | DISABLED
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WebhookDeliveryLog(Base):
    """
    Log of webhook delivery attempts, retries, and Dead Letter Queue (DLQ) records.
    """
    __tablename__ = 'webhook_delivery_logs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey('webhook_subscriptions.id', ondelete='CASCADE'), nullable=False, index=True)
    event_id = Column(String(100), nullable=False)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSONB, default=dict)
    response_code = Column(Integer, nullable=True)
    attempts_count = Column(Integer, default=1)
    status = Column(String(30), default='DELIVERED') # DELIVERED | RETRYING | DEAD_LETTER
    delivered_at = Column(DateTime(timezone=True), server_default=func.now())


class PartnerConnector(Base):
    """
    Configured external enterprise connector (ATS, LMS, University Campus, HRIS).
    """
    __tablename__ = 'partner_connectors'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('recruiter_organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    connector_type = Column(String(50), nullable=False) # ATS | LMS | CAMPUS | HRIS
    name = Column(String(100), nullable=False)
    status = Column(String(30), default='CONNECTED') # CONNECTED | DEGRADED | ERROR | DISCONNECTED
    config = Column(JSONB, default=dict)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    records_synced_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TenantEntitlement(Base):
    """
    Tenant subscription tier, feature entitlements, and metered usage quotas.
    """
    __tablename__ = 'tenant_entitlements'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('recruiter_organizations.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    tier = Column(String(50), default='ENTERPRISE') # STANDARD | BUSINESS | ENTERPRISE | INSTITUTIONAL
    monthly_ai_tokens_quota = Column(Integer, default=1000000)
    used_ai_tokens = Column(Integer, default=0)
    monthly_searches_quota = Column(Integer, default=5000)
    used_searches = Column(Integer, default=0)
    features_enabled = Column(JSONB, default=lambda: ["career_twin", "verified_credentials", "copilot", "simulator", "webhooks"])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class EventOutbox(Base):
    """
    Transactional event buffer implementing the Outbox Pattern for guaranteed event delivery.
    """
    __tablename__ = 'event_outbox'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(100), nullable=False, index=True)
    payload = Column(JSONB, default=dict)
    status = Column(String(30), default='PENDING', index=True) # PENDING | DISPATCHED | FAILED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    dispatched_at = Column(DateTime(timezone=True), nullable=True)


# ==========================================
# PHASE 14: AUTONOMOUS CAREER OPERATING SYSTEM
# ==========================================

class CareerSignal(Base):
    """
    Meaningful career moment signal detected by the Continuous Intelligence loop.
    """
    __tablename__ = 'career_signals'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    signal_type = Column(String(100), nullable=False, index=True) # SKILL_IMPROVEMENT | SKILL_DECAY | NEW_OPPORTUNITY | GOAL_DRIFT | CAREER_RISK
    severity = Column(String(30), default='MEDIUM') # CRITICAL | HIGH | MEDIUM | LOW
    confidence = Column(String(30), default='HIGH') # HIGH | MEDIUM | LOW
    source = Column(String(100), default='CONTINUOUS_INTELLIGENCE')
    details = Column(JSONB, default=dict)
    recommended_action = Column(String(255), nullable=True)
    is_dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)


class NextBestAction(Base):
    """
    Transparently scored and prioritized next career action with explicit explanations.
    """
    __tablename__ = 'next_best_actions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    target_role = Column(String(100), nullable=False)
    action_type = Column(String(50), default='ASSESSMENT') # ASSESSMENT | PROJECT | PRACTICE | VERIFY | APPLY
    title = Column(String(255), nullable=False)
    why_explanation = Column(Text, nullable=False)
    evidence_basis = Column(Text, nullable=False)
    feasibility = Column(String(30), default='HIGHLY_FEASIBLE') # HIGHLY_FEASIBLE | FEASIBLE | DIFFICULT | UNREALISTIC
    estimated_minutes = Column(Integer, default=45)
    action_value_score = Column(Float, default=85.0)
    status = Column(String(30), default='PROPOSED') # PROPOSED | ACCEPTED | SNOOZED | COMPLETED | EXPIRED
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CareerGoalRecord(Base):
    """
    Longitudinal career goal tracking with drift detection and priority hierarchy.
    """
    __tablename__ = 'career_goal_records'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    primary_goal = Column(String(100), nullable=False)
    secondary_goals = Column(JSONB, default=list)
    target_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(30), default='ACTIVE') # ACTIVE | ON_TRACK | AT_RISK | PAUSED | COMPLETED
    health_status = Column(String(50), default='ON_TRACK')
    drift_detected = Column(Boolean, default=False)
    drift_details = Column(JSONB, default=dict)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class EvidenceDispute(Base):
    """
    Formal user dispute workflow for correcting inaccurate or disputed assessment/skill evidence.
    """
    __tablename__ = 'evidence_disputes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    evidence_id = Column(UUID(as_uuid=True), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(30), default='OPEN') # OPEN | UNDER_REVIEW | RESOLVED | REJECTED
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class AutomationPreference(Base):
    """
    User controls for autonomous career engine, notification thresholds, and emergency kill switches.
    """
    __tablename__ = 'automation_preferences'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    autonomy_level = Column(Integer, default=3) # Level 0 (Manual) to Level 4 (Low-risk automatic)
    proactive_recommendations_enabled = Column(Boolean, default=True)
    deadline_alerts_enabled = Column(Boolean, default=True)
    opportunity_alerts_enabled = Column(Boolean, default=True)
    kill_switch_active = Column(Boolean, default=False) # Emergency stop for AI agents
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ============================================================================
# PHASE 15: FINAL CONVERGENCE + PRODUCTION CERTIFICATION + INTELLIGENCE RECEIPT
# ============================================================================

class IntelligenceReceipt(Base):
    """
    Standardized cryptographic receipt for every high-impact AI/analytical output.
    Ensures complete explainability and lineage (Evidence -> Model -> Policy -> Confidence).
    """
    __tablename__ = 'intelligence_receipts'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    decision_type = Column(String(50), nullable=False) # RECOMMENDATION | GAP_DETECTION | READINESS_SCORE | MATCH_SCORE
    output_value = Column(JSONB, nullable=False) # The exact generated recommendation or score payload
    evidence_ids = Column(JSONB, default=list) # List of UUIDs supporting this decision
    model_id = Column(String(50), default='gemini-1.5-flash')
    model_version = Column(String(20), default='15.0.0')
    policy_version = Column(String(20), default='action-ranking-v4')
    confidence_level = Column(String(20), default='HIGH') # HIGH | MEDIUM | LOW | INSUFFICIENT_EVIDENCE
    state = Column(String(20), default='CONFIRMED') # CONFIRMED | PROBABLE | POSSIBLE | UNKNOWN | CONFLICTED | NEEDS_REVIEW | EXPIRED
    user_explanation = Column(Text, nullable=False) # Simplified "Why am I seeing this?"
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AIModelRegistryRecord(Base):
    """
    VIREONIQ Canonical AI Model Registry.
    Tracks all provider models, risk tiers, evaluation scores, average latencies, and costs.
    """
    __tablename__ = 'ai_model_registry_records'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(String(50), unique=True, nullable=False)
    provider = Column(String(50), nullable=False) # Google | Anthropic | OpenAI | Internal AST
    version = Column(String(20), nullable=False)
    purpose = Column(String(100), nullable=False)
    input_types = Column(JSONB, default=list) # ["text", "code", "json"]
    output_types = Column(JSONB, default=list) # ["structured_json", "text"]
    risk_level = Column(String(20), default='LOW') # LOW | MEDIUM | HIGH
    evaluation_score = Column(Float, default=95.0) # Golden test score
    groundedness_score = Column(Float, default=98.0)
    latency_ms_avg = Column(Float, default=320.0)
    cost_per_1k_tokens = Column(Float, default=0.00015)
    status = Column(String(20), default='ACTIVE') # ACTIVE | DEPRECATED | RETIRED
    release_date = Column(DateTime(timezone=True), server_default=func.now())


class ProductionCertificationGate(Base):
    """
    Production Readiness Certification Snapshot for VIREONIQ X RC-1.
    """
    __tablename__ = 'production_certification_gates'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_tag = Column(String(30), default='v15.0.0-rc1')
    security_status = Column(String(20), default='PASS')
    privacy_status = Column(String(20), default='PASS')
    fairness_status = Column(String(20), default='PASS')
    reliability_status = Column(String(20), default='PASS')
    ai_safety_status = Column(String(20), default='PASS')
    ux_accessibility_status = Column(String(20), default='PASS')
    p0_defects_count = Column(Integer, default=0)
    critical_security_defects = Column(Integer, default=0)
    test_pass_rate_pct = Column(Float, default=100.0)
    domain_scorecard = Column(JSONB, default=dict)
    certified_at = Column(DateTime(timezone=True), server_default=func.now())


# ============================================================================
# MNC INTERVIEW & CODING INTELLIGENCE ENGINE DOMAIN MODELS
# ============================================================================

class MNCCompanyInterviewProfile(Base):
    """
    Configurable MNC company interview profiles, round distributions, and evaluation rubrics.
    """
    __tablename__ = 'mnc_company_interview_profiles'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(100), nullable=False, index=True) # e.g. Google, Amazon, Stripe, Generic Tier-1 MNC
    industry = Column(String(100), default='Technology')
    role_family = Column(String(100), default='Software Engineering') # Backend, Full Stack, Frontend, Data, ML, DevOps
    target_level = Column(String(50), default='SDE-2') # Intern, SDE-1, SDE-2, Senior, Staff
    round_configs = Column(JSONB, default=list) # List of configured rounds (0-8)
    skill_weights = Column(JSONB, default=dict) # {"DSA": 0.35, "System Design": 0.25, "Tech Fundamentals": 0.15, ...}
    difficulty_distribution = Column(JSONB, default=dict) # {"EASY": 0.10, "MEDIUM": 0.60, "HARD": 0.30}
    source_policy = Column(String(50), default='PUBLICLY_REPORTED') # GENERATED | PUBLICLY_REPORTED | USER_PROVIDED | AUTHORIZED | SYNTHETIC
    confidence_score = Column(Float, default=95.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MNCQuestionBlueprint(Base):
    """
    Structured blueprint generated prior to question synthesis.
    """
    __tablename__ = 'mnc_question_blueprints'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(String(100), nullable=False)
    level = Column(String(50), default='SDE-2')
    round_type = Column(String(50), default='CODING') # SCREENING | OA | CODING | TECHNICAL | SYSTEM_DESIGN | PROJECT_DEEP_DIVE | BEHAVIORAL | MANAGERIAL
    topic = Column(String(100), nullable=False) # Arrays, Graphs, Dynamic Programming, Caching, STAR Leadership
    difficulty = Column(String(20), default='MEDIUM') # EASY | MEDIUM | HARD | EXPERT
    expected_time_minutes = Column(Integer, default=35)
    evaluation_rubric = Column(JSONB, default=dict) # Criteria: Correctness, Complexity, Edge Cases, Code Quality
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MNCCodingQuestion(Base):
    """
    Full coding problem with statement, constraints, examples, hidden tests, and reference solution.
    """
    __tablename__ = 'mnc_coding_questions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    blueprint_id = Column(UUID(as_uuid=True), ForeignKey('mnc_question_blueprints.id', ondelete='SET NULL'), nullable=True)
    title = Column(String(255), nullable=False)
    problem_statement = Column(Text, nullable=False)
    constraints = Column(JSONB, default=list) # List of constraints e.g. ["1 <= n <= 10^5", "-10^9 <= nums[i] <= 10^9"]
    examples = Column(JSONB, default=list) # [{"input": "[2,7,11,15], target=9", "output": "[0,1]", "explanation": "..."}]
    public_test_cases = Column(JSONB, default=list)
    hidden_test_cases = Column(JSONB, default=list) # Never sent to client before evaluation
    reference_solutions = Column(JSONB, default=dict) # {"python": "def solution()...", "java": "..."}
    expected_time_complexity = Column(String(50), default='O(N)')
    expected_space_complexity = Column(String(50), default='O(N)')
    acceptable_complexity_range = Column(String(100), default='O(N) to O(N log N)')
    edge_cases = Column(JSONB, default=list) # ["Empty array", "Negative numbers", "Duplicates", "Integer overflow"]
    skill_tags = Column(JSONB, default=list) # ["Hashing", "Two Pointers", "Arrays"]
    difficulty = Column(String(20), default='MEDIUM')
    source_type = Column(String(50), default='GENERATED') # GENERATED | PUBLICLY_REPORTED | SYNTHETIC | AUTHORIZED
    validation_status = Column(String(30), default='APPROVED') # DRAFT | VALIDATING | APPROVED | ACTIVE | AGING | RETIRED
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MNCInterviewSession(Base):
    """
    MNC Multi-Round Interactive Interview Session.
    """
    __tablename__ = 'mnc_interview_sessions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    profile_id = Column(UUID(as_uuid=True), ForeignKey('mnc_company_interview_profiles.id', ondelete='SET NULL'), nullable=True)
    target_company = Column(String(100), default='Generic Tier-1 MNC')
    target_role = Column(String(100), nullable=False)
    target_level = Column(String(50), default='SDE-2')
    current_round_index = Column(Integer, default=1) # 0 to 8
    total_rounds = Column(Integer, default=4)
    mode = Column(String(30), default='ASSESSMENT') # ASSESSMENT | PRACTICE | COMPANY_SIMULATION
    status = Column(String(30), default='IN_PROGRESS') # NOT_STARTED | IN_PROGRESS | PAUSED | COMPLETED | EVALUATED | REVIEWED
    overall_score = Column(Float, nullable=True) # 0 to 100
    dimension_scores = Column(JSONB, default=dict) # {"coding": 92.0, "system_design": 88.0, "behavioral": 90.0, ...}
    coverage_matrix = Column(JSONB, default=dict) # {"Arrays": True, "Trees": True, "System Design": True}
    session_receipt_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class MNCInterviewTurn(Base):
    """
    Individual conversational question-answer-followup turn within an interview session.
    """
    __tablename__ = 'mnc_interview_turns'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('mnc_interview_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    turn_number = Column(Integer, default=1)
    round_type = Column(String(50), default='TECHNICAL')
    question_text = Column(Text, nullable=False)
    question_category = Column(String(50), default='TECHNICAL') # TECHNICAL | CODING | SYSTEM_DESIGN | PROJECT_DEEP_DIVE | BEHAVIORAL | FOLLOW_UP
    candidate_response = Column(Text, nullable=True)
    follow_up_prompt = Column(Text, nullable=True) # Dynamic branch question generated in response
    evaluation_scores = Column(JSONB, default=dict) # {"technical_depth": 90, "clarity": 85, "star_adherence": 92}
    evaluated_complexity = Column(String(50), nullable=True) # e.g. O(N log N) from AST
    proctor_signals = Column(JSONB, default=dict) # {"paste_burst": False, "tab_switches": 0}
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class QuestionQualityMetric(Base):
    """
    Continuous item analysis and quality tracking for interview questions.
    """
    __tablename__ = 'question_quality_metrics'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    total_attempts = Column(Integer, default=0)
    passed_attempts = Column(Integer, default=0)
    avg_completion_time_seconds = Column(Float, default=0.0)
    discrimination_index = Column(Float, default=0.75) # Ability to separate strong vs weak candidates
    ambiguity_reports_count = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())














