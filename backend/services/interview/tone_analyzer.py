import re
from typing import Dict, Any

FILLER_WORDS = {"um", "uh", "like", "you know", "basically", "actually", "literally"}
HEDGING_WORDS = {"i think", "maybe", "probably", "might", "could", "sort of", "kind of", "somewhat", "perhaps"}

def analyze_tone_and_confidence(text: str) -> Dict[str, Any]:
    """
    Analyzes candidate speech/text for confidence markers, hedging, and cognitive load.
    Returns metrics that feed into the RL reward signal and final scorecard.
    """
    text_lower = text.lower()
    words = text_lower.split()
    word_count = len(words)
    
    if word_count == 0:
        return {"filler_count": 0, "hedging_count": 0, "cognitive_load_score": 0.0}

    # Count Fillers (exact word matches for single words, substring for phrases)
    filler_count = 0
    for filler in FILLER_WORDS:
        if " " in filler:
            filler_count += text_lower.count(filler)
        else:
            filler_count += words.count(filler)
            
    # Count Hedging
    hedging_count = 0
    for hedge in HEDGING_WORDS:
        if " " in hedge:
            hedging_count += text_lower.count(hedge)
        else:
            hedging_count += words.count(hedge)

    # Cognitive Load heuristic: high word count but many fillers/hedging implies high load
    # Plus repetition of words (stuttering effect)
    unique_words = len(set(words))
    repetition_ratio = 1.0 - (unique_words / word_count) if word_count > 0 else 0
    
    # Scale 0 to 10. Higher means more load (worse).
    cognitive_load = min(10.0, (filler_count * 0.5) + (hedging_count * 0.8) + (repetition_ratio * 10))

    return {
        "filler_count": filler_count,
        "hedging_count": hedging_count,
        "cognitive_load_score": round(cognitive_load, 2)
    }
