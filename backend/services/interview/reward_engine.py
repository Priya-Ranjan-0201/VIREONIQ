from decimal import Decimal
from typing import Dict, Any

def calculate_interview_reward(
    evaluation: Dict[str, Any],
    tone_metrics: Dict[str, Any],
    latency_ms: int,
    turn_number: int
) -> Decimal:
    """
    Calculates a reward signal for the RL agent based on candidate performance.
    Range: -1.0 to 1.0
    """
    # 1. Base score from LLM evaluation (0-100)
    tech_score = float(evaluation.get("technical_correctness", 50)) / 100.0
    comm_score = float(evaluation.get("communication_clarity", 50)) / 100.0
    
    # 2. Tone Penalties
    hedging_penalty = float(tone_metrics.get("hedging_count", 0)) * 0.05
    load_penalty = (float(tone_metrics.get("cognitive_load", 0.5)) - 0.3) * 0.2 # Penalty if load > 0.3
    
    # 3. Latency Bonus/Penalty
    # Ideal latency for a balanced answer is between 5s and 30s
    latency_seconds = latency_ms / 1000.0
    latency_factor = 0.0
    if latency_seconds < 2.0: # Too fast, likely short/no-thought
        latency_factor = -0.1
    elif latency_seconds > 45.0: # Too slow
        latency_factor = -0.1
    else:
        latency_factor = 0.05
        
    # 4. Aggregate
    reward = (tech_score * 0.5) + (comm_score * 0.3) + latency_factor - hedging_penalty - load_penalty
    
    # Normalize to -1.0 to 1.0
    return Decimal(str(max(-1.0, min(1.0, reward))))
