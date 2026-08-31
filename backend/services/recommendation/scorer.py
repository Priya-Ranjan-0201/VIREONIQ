from typing import Dict, Any, Optional
from db.models import User, JobListing, Resume, InterviewScore, GapAnalysis

def get_base_scores(
    user: User, 
    job: JobListing, 
    resume: Optional[Resume], 
    interview: Optional[InterviewScore], 
    gap: Optional[GapAnalysis]
) -> Dict[str, Any]:
    """
    Calculates raw scores across dimensions.
    """
    # 1. Skill Fit (Resume vs Job)
    skill_fit = 0.5 # Default
    if resume and job.required_skills:
        user_skills = set(resume.parsed_data.get("skills", "").lower().split(","))
        job_skills = set(job.required_skills.lower().split(","))
        if job_skills:
            intersection = user_skills.intersection(job_skills)
            skill_fit = len(intersection) / len(job_skills)

    # 2. Interview Fit
    interview_fit = float(interview.overall_score) / 100 if interview else 0.5
    
    # 3. Gap Readiness
    gap_fit = float(gap.overall_readiness_score) / 100 if gap else 0.5
    
    # Final Match Score (40/30/30 weights)
    final_score = (skill_fit * 0.4) + (interview_fit * 0.3) + (gap_fit * 0.3)
    
    # Freshers / Startup boost
    if job.company_tier == "Startup" and user.role == "student":
        final_score *= 1.1
        
    return {
        "final_match_score": min(100, final_score * 100),
        "skill_fit": skill_fit * 100,
        "interview_fit": interview_fit * 100,
        "gap_fit": gap_fit * 100
    }
