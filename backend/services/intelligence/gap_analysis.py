from typing import Dict, List, Any
import numpy as np

class GapAnalysisEngine:
    """
    The 5-Dimensional Intelligence Engine.
    Tracks: Skill, Knowledge, Confidence, Experience, Communication.
    """
    
    def __init__(self):
        self.dimensions = ["Skill", "Knowledge", "Confidence", "Experience", "Communication"]

    def calculate_current_profile(self, interview_history: List[Dict]) -> Dict[str, float]:
        """
        Aggregates raw telemetry and evaluation data into the 5D Profile.
        """
        if not interview_history:
            return {d: 0.5 for d in self.dimensions}

        # Initialize aggregators
        scores = {d: [] for d in self.dimensions}

        for session in interview_history:
            # 1. Skill (Technical performance in evaluations)
            scores["Skill"].append(session.get("tech_score", 0.5))
            
            # 2. Knowledge (Concept depth)
            scores["Knowledge"].append(session.get("depth_score", 0.5))
            
            # 3. Confidence (Latency/Telemetry - lower latency = higher confidence)
            telemetry = session.get("telemetry", {})
            latency = telemetry.get("avg_latency", 500) # ms
            # Normalize: 100ms = 1.0, 2000ms = 0.0
            confidence = max(0, min(1, (2000 - latency) / 1900))
            scores["Confidence"].append(confidence)
            
            # 4. Experience (Contextual awareness/Scenario handling)
            scores["Experience"].append(session.get("scenario_score", 0.5))
            
            # 5. Communication (Articulation/Sentiment)
            scores["Communication"].append(session.get("comm_score", 0.5))

        return {
            d: round(float(np.mean(vals)), 2) if vals else 0.5 
            for d, vals in scores.items()
        }

    def identify_critical_gaps(self, profile: Dict[str, float], target_benchmark: float = 0.8) -> List[Dict]:
        """
        Identifies dimensions below the hiring benchmark.
        """
        gaps = []
        for dim, value in profile.items():
            if value < target_benchmark:
                gaps.append({
                    "dimension": dim,
                    "score": value,
                    "gap": round(target_benchmark - value, 2),
                    "urgency": "High" if (target_benchmark - value) > 0.3 else "Medium"
                })
        return sorted(gaps, key=lambda x: x["gap"], reverse=True)

    def get_market_alignment(self, profile: Dict[str, float], market_trends: Dict) -> float:
        """
        Calculates how 'hirable' the candidate is based on current market signals.
        """
        # Weighted average based on what the market currently values (e.g. Skill > Communication)
        weights = {
            "Skill": 0.35,
            "Knowledge": 0.20,
            "Experience": 0.25,
            "Communication": 0.15,
            "Confidence": 0.05
        }
        
        alignment = sum(profile[d] * weights[d] for d in self.dimensions)
        return round(alignment, 2)
