# VIREONIQ — Comprehensive Feature & Endpoint Inventory

> **Version**: Phase L1 Staged Launch Baseline  
> **Methodology**: Automated AST and source scan across all 73 frontend pages and 75 backend endpoint modules.  
> **Tiers**:  
> - **Tier 1 (Public Beta)**: Fully hardened core user journeys (ATS, Resume, Interview, Readiness, Auth).  
> - **Tier 2 (Invite-Only Flagged)**: Advanced simulation, career planning, credentials, and gamification behind feature gates.  
> - **Tier 3 (Review Gated / Hidden)**: Employment-decision, minor-related, community/truth, and administrative dashboards withheld until formal counsel review.  

---

## 1. Frontend Page Inventory (73 Modules)

| Page File | Status | Data Source | Owner-Visible Risks | Recommended Launch Tier |
|:---|:---|:---|:---|:---|
| analytics\BenchmarkReportPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| analytics\CalendarExportPage.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| analytics\MarketIntelligencePage.tsx | Simulated / Sample Data | Local React State / Sample Fixtures | Sample data presentation risk; requires explicit preview badge | **Tier 2 (Invite-Only Flagged)** |
| analytics\OutcomeIntelligencePage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| analytics\SkillDecayPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| ApplicationIntelligence.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| assessment\AssessmentRoomPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| auth\LoginPage.tsx | Real (API Wired) | JWT / Argon2id DB | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| auth\RegisterPage.tsx | Real (API Wired) | JWT / Argon2id DB | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| billing\PricingPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| career\CareerControlCenterPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| career\CareerGPSPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| career\CareerTwinPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| career\PortfolioIntelligence.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| career\SalaryPredictor.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| CareerRebirth.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 3 (Hidden / Review Gated)** |
| certification\ProductionCertificationPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| CohortMode.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 3 (Hidden / Review Gated)** |
| college\CollegeAdminDashboard.tsx | Simulated / Sample Data | Local React State / Sample Fixtures | Sample data presentation risk; requires explicit preview badge | **Tier 3 (Hidden / Review Gated)** |
| CommunityHub.tsx | Real (API Wired) | FastAPI /api/v1 Backend | User-generated content defamation & unmoderated employer review risk | **Tier 3 (Hidden / Review Gated)** |
| companies\companyProfilesData.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| companies\CompanyProfilesPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| copilot\AICopilotPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| CredentialProfile.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| dashboard\DashboardPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| developer\DeveloperPlatformPage.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 3 (Hidden / Review Gated)** |
| EarnToLearn.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 3 (Hidden / Review Gated)** |
| EmployerTruthScore.tsx | Real (API Wired) | FastAPI /api/v1 Backend | User-generated content defamation & unmoderated employer review risk | **Tier 3 (Hidden / Review Gated)** |
| FacultyDashboard.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 3 (Hidden / Review Gated)** |
| gamification\GamificationPage.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| gamification\LeaderboardPage.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| gap\GapAnalysisPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| HighSchoolTrajectory.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Minor privacy & parental consent compliance risk (DPDP / COPPA) | **Tier 3 (Hidden / Review Gated)** |
| interventions\CareerOSPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| interview\CodingInterviewPage.tsx | UI Form / Heuristic | Interview Service / Judge0 | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| interview\CognitiveLoadMonitorPage.tsx | Simulated / Sample Data | Interview Service / Judge0 | Sample data presentation risk; requires explicit preview badge | **Tier 1 (Public Beta)** |
| interview\InterviewPage.tsx | UI Form / Heuristic | Interview Service / Judge0 | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| interview\MNCInterviewStudioPage.tsx | UI Form / Heuristic | Interview Service / Judge0 | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| interview\P2PMockPage.tsx | UI Form / Heuristic | JWT / Argon2id DB | Standard SaaS data handling & rate limiting | **Tier 3 (Hidden / Review Gated)** |
| interview\VoiceInterviewPage.tsx | UI Form / Heuristic | Interview Service / Judge0 | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| jobs\ApplicationDetail.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| jobs\components\OpportunityStats.tsx | UI Form / Heuristic | Resume Parser / ATS Rubric | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| jobs\OfferComparator.tsx | Simulated / Sample Data | Local React State / Sample Fixtures | Sample data presentation risk; requires explicit preview badge | **Tier 2 (Invite-Only Flagged)** |
| jobs\OfferNegotiatorPage.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| jobs\OpportunityHub.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| jobs\SmartApplyTracker.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| LabMode.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 3 (Hidden / Review Gated)** |
| LanguageBridge.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| learning\MicroInternships.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 3 (Hidden / Review Gated)** |
| learning\SyllabusOptimizer.tsx | Simulated / Sample Data | Local React State / Sample Fixtures | Sample data presentation risk; requires explicit preview badge | **Tier 3 (Hidden / Review Gated)** |
| MentorNetwork.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| MyCredential.tsx | Heuristic + Sample Fallback | FastAPI /api/v1 Backend | Sample data presentation risk; requires explicit preview badge | **Tier 2 (Invite-Only Flagged)** |
| OfflinePractice.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| parent\ParentDashboard.tsx | Simulated / Sample Data | Local React State / Sample Fixtures | Minor privacy & parental consent compliance risk (DPDP / COPPA) | **Tier 3 (Hidden / Review Gated)** |
| ParentConnect.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Minor privacy & parental consent compliance risk (DPDP / COPPA) | **Tier 3 (Hidden / Review Gated)** |
| passport\PublicVerificationPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| passport\TalentPassportPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| privacy\PrivacySettingsPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| psychometric\PsychometricDNAPage.tsx | Simulated / Sample Data | Local React State / Sample Fixtures | Unvalidated personality profiling / lack of psychometric psychometric validation | **Tier 3 (Hidden / Review Gated)** |
| recruiter\RecruiterDashboard.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | High-risk automated employment decision (EU AI Act Annex III / NYC LL144); candidate consent required | **Tier 3 (Hidden / Review Gated)** |
| recruiter\RecruiterIntelligencePage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | High-risk automated employment decision (EU AI Act Annex III / NYC LL144); candidate consent required | **Tier 3 (Hidden / Review Gated)** |
| recruiter\WarRoom.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | High-risk automated employment decision (EU AI Act Annex III / NYC LL144); candidate consent required | **Tier 3 (Hidden / Review Gated)** |
| resume\AtsScoreChecker.tsx | UI Form / Heuristic | Resume Parser / ATS Rubric | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| resume\JdMatcher.tsx | UI Form / Heuristic | Resume Parser / ATS Rubric | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| resume\ResumeScorePage.tsx | Real (API Wired) | Resume Parser / ATS Rubric | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| resume\ResumeSectionRewriterPage.tsx | Simulated / Sample Data | Resume Parser / ATS Rubric | Sample data presentation risk; requires explicit preview badge | **Tier 1 (Public Beta)** |
| ResumeBuilder.tsx | Real (API Wired) | Resume Parser / ATS Rubric | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| settings\SettingsPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 1 (Public Beta)** |
| simulator\CareerSimulatorPage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| TalentPassport.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 2 (Invite-Only Flagged)** |
| TruthDatabase.tsx | Real (API Wired) | FastAPI /api/v1 Backend | User-generated content defamation & unmoderated employer review risk | **Tier 3 (Hidden / Review Gated)** |
| VernacularLibrary.tsx | Real (API Wired) | FastAPI /api/v1 Backend | Standard SaaS data handling & rate limiting | **Tier 3 (Hidden / Review Gated)** |
| workforce\WorkforceIntelligencePage.tsx | UI Form / Heuristic | Local React State / Sample Fixtures | High-risk automated employment decision (EU AI Act Annex III / NYC LL144); candidate consent required | **Tier 3 (Hidden / Review Gated)** |

---

## 2. Backend Endpoint Modules Inventory (75 Modules)

| Endpoint Module | Status | Data Source | Owner-Visible Risks | Recommended Launch Tier |
|:---|:---|:---|:---|:---|
| pi/api_v1/endpoints/admin.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/advanced_modes.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/ai_observability.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/ai_orchestration.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/analytics.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/assessments.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/auth.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 1 (Public Beta)** |
| pi/api_v1/endpoints/autonomous_os.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/battlefield.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/bias_detector.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/calendar.py | Real (DB + LLM) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/career_goals.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/career_rebirth.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/career_simulator.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/career_twin.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/code.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | Untrusted code execution sandbox escape risk | **Tier 1 (Public Beta)** |
| pi/api_v1/endpoints/cohorts.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/college.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/community.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | Defamation / unmoderated user claims | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/companies.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/convergence_certification.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/credentials.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/crm.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/cybersecurity.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/earn_to_learn.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/employer_b2b.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/employer_truth.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | Defamation / unmoderated user claims | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/extended_features.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/faculty.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/gamification.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/gap.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 1 (Public Beta)** |
| pi/api_v1/endpoints/global_parity.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/health.py | Real (DB + LLM) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/highschool.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | Minor data collection without parental verification | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/internships.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/interventions.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/interview.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 1 (Public Beta)** |
| pi/api_v1/endpoints/market.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/matchmaker.py | Heuristic / Static Service | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/mentors.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/meta_game.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/missions.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/mnc_interview.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 1 (Public Beta)** |
| pi/api_v1/endpoints/multilingual.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/notifications.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/offers.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/offline_sync.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/outcomes_analytics.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/parent.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | Minor data collection without parental verification | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/parent_link.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | Minor data collection without parental verification | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/passport.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/payments.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | Webhook idempotency & transaction reconciliation | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/platform_developer.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/pressure.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/privacy_security.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/psychometric.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/readiness.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 1 (Public Beta)** |
| pi/api_v1/endpoints/recommendations.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/recruiter.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | Automated candidate filtering & ranking legal liability | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/recruiter_intelligence.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | Automated candidate filtering & ranking legal liability | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/referral_economy.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | Defamation / unmoderated user claims | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/reports.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/resume.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 1 (Public Beta)** |
| pi/api_v1/endpoints/resume_ab.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 1 (Public Beta)** |
| pi/api_v1/endpoints/resume_builder.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 1 (Public Beta)** |
| pi/api_v1/endpoints/rl.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/roi_gaps.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 1 (Public Beta)** |
| pi/api_v1/endpoints/roles_intelligence.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/skill_decay.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 2 (Invite-Only Flagged)** |
| pi/api_v1/endpoints/skills_evidence.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 1 (Public Beta)** |
| pi/api_v1/endpoints/syllabus.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/truth_database.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | Defamation / unmoderated user claims | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/vernacular_library.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | IDOR / tenant isolation & rate limit management | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/war_room.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | Automated candidate filtering & ranking legal liability | **Tier 3 (Hidden / Review Gated)** |
| pi/api_v1/endpoints/workforce_intelligence.py | Real (PostgreSQL / SQLite) | FastAPI / SQLAlchemy / Celery | Automated candidate filtering & ranking legal liability | **Tier 3 (Hidden / Review Gated)** |

---

## 3. Launch Tier Summary & Action Matrix

### Tier 1: Public Beta (Active for Public Launch)
- **Candidate Core**: Signup, login, password security, session management.
- **Resume & ATS Studio**: ATS rubric calculator, bullet point optimizer, section rewriter, company profile criteria.
- **Interview Studio**: General interview practice, coding interview with sandbox, MNC interview memory.
- **Readiness Analysis**: Honest readiness scoring without fabricated hiring probability guarantees.

### Tier 2: Invite-Only / Beta Flagged (Behind Feature Flags)
- **Career Planning**: Career Simulator (what-if scenarios), Career GPS navigator.
- **Application Management**: Smart Apply tracker, offer comparison, offer negotiation.
- **Growth & Learning**: Syllabus optimizer, micro-internships, skill decay tracker, prep calendar.
- **Gamification & Credentials**: Streaks, XP badges, Talent Passport (HMAC-backed).

### Tier 3: Review Gated / Hidden (Disabled Until Counsel & Compliance Sign-Off)
- **Recruiter & Workforce Intelligence**: Multi-tenant candidate ranking, War Room, talent discovery (EU AI Act Annex III / NYC LL144 high-risk compliance required).
- **Minor & Institutional Tools**: High School Trajectory, Parent Dashboard, Parent Link, College Admin, Faculty Dashboard (parental consent & student data privacy required).
- **Community & Employer Ratings**: Employer Truth Score, Truth Database, Community Hub (defamation & moderation infrastructure required).
- **Specialized Sandboxes**: Psychometric DNA, Developer Platform API keys, Lab Mode, Cohort Mode, P2P Mock.
