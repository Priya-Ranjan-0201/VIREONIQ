from typing import List, Optional
from db.models import JobListing, UserPreference

def apply_hard_filters(jobs: List[JobListing], prefs: Optional[UserPreference]) -> List[JobListing]:
    if not prefs:
        return jobs
        
    filtered = []
    for job in jobs:
        # Remote check
        if prefs.remote_only and not job.is_remote:
            continue
            
        # Salary check
        if prefs.min_salary_target and job.salary_max and job.salary_max < prefs.min_salary_target:
            continue
            
        # Role check (Partial string match on target roles)
        if prefs.target_roles:
            target_roles = [r.lower() for r in prefs.target_roles.split(",")]
            if not any(role in job.title.lower() for role in target_roles):
                continue
                
        filtered.append(job)
    
    return filtered
