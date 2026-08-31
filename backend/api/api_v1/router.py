from fastapi import APIRouter
from api.api_v1.endpoints import (
    auth, resume, gap, interview, recommendations, crm, payments, analytics,
    notifications, calendar, code, offers, reports, recruiter, matchmaker,
    syllabus, internships, rl, gamification, skill_decay, psychometric,
     companies, market, college, parent,
     extended_features, cybersecurity, advanced_modes, meta_game,
     employer_b2b, resume_ab, admin,
     credentials, career_rebirth, multilingual, bias_detector, mentors,
     truth_database, referral_economy, highschool, employer_truth, global_parity,
     community, resume_builder,
      offline_sync, faculty, earn_to_learn, parent_link, pressure, cohorts, war_room, vernacular_library,
      readiness, skills_evidence, roi_gaps, missions, career_simulator, ai_observability,
      career_twin, career_goals, roles_intelligence, assessments, interventions,
      credentials, passport, recruiter_intelligence, workforce_intelligence, ai_orchestration,
       privacy_security, outcomes_analytics, platform_developer, autonomous_os,
       convergence_certification, mnc_interview
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(mnc_interview.router, prefix="/mnc-interview", tags=["mnc-interview"])
api_router.include_router(convergence_certification.router, prefix="/certification", tags=["certification"])
api_router.include_router(autonomous_os.router, prefix="/career-os", tags=["career-os"])
api_router.include_router(platform_developer.router, prefix="/platform", tags=["platform-developer"])
api_router.include_router(outcomes_analytics.router, prefix="/outcomes", tags=["outcomes"])
api_router.include_router(privacy_security.router, prefix="/privacy-security", tags=["privacy-security"])
api_router.include_router(ai_orchestration.router, prefix="/ai", tags=["ai-orchestration"])
api_router.include_router(workforce_intelligence.router, prefix="/org", tags=["workforce-intelligence"])
api_router.include_router(recruiter_intelligence.router, prefix="/recruiter-intel", tags=["recruiter-intel"])
api_router.include_router(passport.router, prefix="/passport", tags=["passport"])
api_router.include_router(credentials.router, prefix="/credentials", tags=["credentials"])
api_router.include_router(interventions.router, prefix="/interventions", tags=["interventions"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
api_router.include_router(career_twin.router, prefix="/career-twin", tags=["career-twin"])
api_router.include_router(career_goals.router, prefix="/career-goals", tags=["career-goals"])
api_router.include_router(roles_intelligence.router, prefix="/roles-intelligence", tags=["roles-intelligence"])
api_router.include_router(readiness.router, prefix="/readiness", tags=["readiness"])
api_router.include_router(skills_evidence.router, prefix="/skills", tags=["skills"])
api_router.include_router(roi_gaps.router, prefix="/roi-gaps", tags=["roi-gaps"])
api_router.include_router(missions.router, prefix="/missions", tags=["missions"])
api_router.include_router(career_simulator.router, prefix="/career-simulator", tags=["career-simulator"])
api_router.include_router(ai_observability.router, prefix="/ai-observability", tags=["ai-observability"])

api_router.include_router(resume.router, prefix="/resume", tags=["resume"])
api_router.include_router(gap.router, prefix="/gap", tags=["gap"])
api_router.include_router(interview.router, prefix="/interview", tags=["interview"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(crm.router, prefix="/crm", tags=["crm"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(code.router, prefix="/code", tags=["code"])
api_router.include_router(offers.router, prefix="/offers", tags=["offers"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(recruiter.router, prefix="/recruiter", tags=["recruiter"])
api_router.include_router(matchmaker.router, prefix="/ws", tags=["matchmaker"])
api_router.include_router(syllabus.router, prefix="/syllabus", tags=["syllabus"])
api_router.include_router(internships.router, prefix="/internships", tags=["internships"])
api_router.include_router(rl.router, prefix="/rl", tags=["rl"])
api_router.include_router(gamification.router, prefix="/gamification", tags=["gamification"])
api_router.include_router(skill_decay.router, prefix="/skill-decay", tags=["skill-decay"])
api_router.include_router(psychometric.router, prefix="/psychometric", tags=["psychometric"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(market.router, prefix="/market", tags=["market"])
api_router.include_router(college.router, prefix="/college", tags=["college"])
api_router.include_router(parent.router, prefix="/parent", tags=["parent"])
api_router.include_router(extended_features.router, prefix="/extended", tags=["extended"])
api_router.include_router(cybersecurity.router, prefix="/cybersecurity", tags=["cybersecurity"])
api_router.include_router(advanced_modes.router, prefix="/advanced", tags=["advanced"])
api_router.include_router(meta_game.router, prefix="/meta-game", tags=["meta-game"])
api_router.include_router(employer_b2b.router, prefix="/employer-b2b", tags=["employer-b2b"])
api_router.include_router(resume_ab.router, prefix="/resume-ab", tags=["resume-ab"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(credentials.router, prefix="/credentials", tags=["credentials"])
api_router.include_router(career_rebirth.router, prefix="/rebirth", tags=["rebirth"])
api_router.include_router(multilingual.router, prefix="/multilingual", tags=["multilingual"])
api_router.include_router(bias_detector.router, prefix="/routing", tags=["routing"])
api_router.include_router(mentors.router, prefix="/mentors", tags=["mentors"])
api_router.include_router(truth_database.router, prefix="/truth", tags=["truth"])
api_router.include_router(referral_economy.router, prefix="/referrals", tags=["referrals"])
api_router.include_router(highschool.router, prefix="/highschool", tags=["highschool"])
api_router.include_router(employer_truth.router, prefix="/employer-truth", tags=["employer-truth"])
api_router.include_router(global_parity.router, prefix="/global", tags=["global"])
api_router.include_router(community.router, prefix="/community", tags=["community"])
api_router.include_router(resume_builder.router, prefix="/resume-builder", tags=["resume-builder"])
api_router.include_router(offline_sync.router, prefix="/offline", tags=["offline-sync"])
api_router.include_router(faculty.router, prefix="/faculty", tags=["faculty"])
api_router.include_router(earn_to_learn.router, prefix="/earn", tags=["earn-to-learn"])
api_router.include_router(parent_link.router, prefix="/parent-link", tags=["parent-link"])
api_router.include_router(pressure.router, prefix="/pressure", tags=["pressure-pacing"])
api_router.include_router(cohorts.router, prefix="/cohorts", tags=["cohort-mode"])
api_router.include_router(war_room.router, prefix="/war-room", tags=["war-room"])
api_router.include_router(vernacular_library.router, prefix="/vernacular", tags=["vernacular-library"])

@api_router.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "ok", "message": "VIREONIQ API is running."}
