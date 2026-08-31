from typing import Dict, Any, Optional
from db.models import User, JobListing, Resume, InterviewScore

def generate_match_explanation(
    user: User, 
    job: JobListing, 
    resume: Optional[Resume], 
    interview: Optional[InterviewScore],
    scores: Dict[str, Any]
) -> Dict[str, Any]:
    reasons = []
    missing = []
    
    # Technical reasons
    if scores["skill_fit"] > 70:
        reasons.append("Strong technical alignment with core stack")
    elif scores["skill_fit"] < 40:
        missing.append("Significant technical skill mismatch")
        
    # Interview reasons
    if interview and float(interview.overall_score) > 80:
        reasons.append("High interview confidence score in this domain")
        
    # Job specifics
    if job.is_remote:
        reasons.append("Matches your remote-first preference")
        
    # Skill gaps
    if resume and job.required_skills:
        user_skills = set(resume.parsed_data.get("skills", "").lower().split(","))
        job_skills = set(job.required_skills.lower().split(","))
        diff = job_skills - user_skills
        missing.extend(list(diff)[:3])

    return {
        "reasons": reasons if reasons else ["General role alignment"],
        "missing_blockers": missing
    }
