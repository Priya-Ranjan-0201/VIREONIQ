from db.models import JobListing

def calculate_offer_probability(skill_fit: float, job: JobListing, interview_fit: float) -> float:
    """
    Predicts likelihood of an actual offer.
    Factors in competition and interview confidence.
    """
    # Competition penalty
    penalty = (job.competition_index or 0.5) * 20 # Up to 20% reduction
    
    # Interview weight is higher for offer probability than for simple matching
    prob = (skill_fit * 0.3) + (interview_fit * 0.7)
    
    final_prob = prob - penalty
    return max(0, min(100, final_prob))

def get_confidence_level(score: float) -> str:
    if score > 85: return "High"
    if score > 60: return "Medium"
    return "Low"
