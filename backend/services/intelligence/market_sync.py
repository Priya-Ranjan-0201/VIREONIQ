from typing import Dict, List, Any
import random

class MarketSyncEngine:
    """
    Market Synchronicity & Hiring Probability Engine.
    Aligns candidate DNA with Company-specific rubrics.
    """
    
    # Historical 'DNA' of successful hires at top firms
    COMPANY_DNA = {
        "Google": {"Skill": 0.90, "Knowledge": 0.85, "Experience": 0.70, "Communication": 0.70, "Confidence": 0.80},
        "Amazon": {"Skill": 0.80, "Knowledge": 0.70, "Experience": 0.90, "Communication": 0.75, "Confidence": 0.85}, # Heavy on Ownership (Experience)
        "Meta": {"Skill": 0.95, "Knowledge": 0.75, "Experience": 0.80, "Communication": 0.70, "Confidence": 0.70}, # Heavy on Speed (Skill)
        "FastGrowth_Startup": {"Skill": 0.75, "Knowledge": 0.60, "Experience": 0.95, "Communication": 0.85, "Confidence": 0.90}
    }

    def calculate_hiring_probability(self, profile: Dict[str, float], company: str) -> Dict[str, Any]:
        """
        Calculates how likely a candidate is to pass the 'Bar Raiser' at a specific company.
        """
        target_dna = self.COMPANY_DNA.get(company)
        if not target_dna:
            # Fallback to generic high-tier startup DNA
            target_dna = self.COMPANY_DNA["FastGrowth_Startup"]
            
        # Weighted matching
        match_score = 0
        weights = {"Skill": 0.3, "Knowledge": 0.2, "Experience": 0.2, "Communication": 0.2, "Confidence": 0.1}
        
        reasons = []
        missing = []
        
        for dim, target_val in target_dna.items():
            user_val = profile.get(dim, 0)
            if user_val >= target_val:
                match_score += weights[dim]
                reasons.append(f"Strong {dim} alignment.")
            else:
                # Partial credit
                match_score += (user_val / target_val) * weights[dim]
                if (target_val - user_val) > 0.2:
                    missing.append(dim)
                    
        probability = round(match_score * 100, 1)
        
        return {
            "company": company,
            "probability": probability,
            "alignment_reasons": reasons[:2],
            "critical_missing": missing,
            "market_velocity": "Increasing" if probability > 70 else "Stable"
        }

    def get_market_opportunities(self, profile: Dict[str, float]) -> List[Dict]:
        """
        Scans the 'Market' for companies where the candidate has > 70% probability.
        """
        opportunities = []
        for company in self.COMPANY_DNA:
            res = self.calculate_hiring_probability(profile, company)
            if res["probability"] > 60:
                opportunities.append(res)
        
        return sorted(opportunities, key=lambda x: x["probability"], reverse=True)
