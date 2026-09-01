import re
from typing import Dict, Any

FILLER_WORDS = {
    "um", "uh", "er", "ah", "like", "you know", "basically", "actually",
    "literally", "sort of", "kind of", "i mean", "honestly", "to be honest"
}

HEDGING_WORDS = {
    "i think", "maybe", "probably", "might", "could", "sort of", "kind of",
    "somewhat", "perhaps", "i guess", "not totally sure", "i believe", "possibly", "presumably"
}

STRUCTURAL_MARKERS = {
    "first", "firstly", "second", "secondly", "third", "furthermore", "in addition",
    "specifically", "for example", "for instance", "in contrast", "as a result",
    "consequently", "in conclusion", "tradeoff", "retrospective"
}

def analyze_tone_and_confidence(text: str) -> Dict[str, Any]:
    """
    Analyzes candidate speech/text for confidence markers, hedging, discourse structure,
    and cognitive load. Returns metrics that feed into the RL reward signal and final scorecard.
    """
    text_lower = (text or "").lower()
    words = re.findall(r"\b[a-z']+\b", text_lower)
    word_count = len(words)
    
    if word_count == 0:
        return {
            "filler_count": 0,
            "hedging_count": 0,
            "cognitive_load_score": 0.0,
            "confidence_score": 50.0,
            "structural_markers_count": 0,
            "pacing_feedback": "No speech/text detected."
        }

    # Count Fillers
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

    # Count Structural Markers
    structural_count = 0
    for marker in STRUCTURAL_MARKERS:
        if " " in marker:
            structural_count += text_lower.count(marker)
        else:
            structural_count += words.count(marker)

    # Cognitive Load heuristic: high word count but many fillers/hedging implies high load
    unique_words = len(set(words))
    repetition_ratio = 1.0 - (unique_words / word_count) if word_count > 0 else 0
    
    # Scale 0 to 10. Higher means more load (worse).
    filler_ratio = filler_count / max(word_count, 1)
    hedge_ratio = hedging_count / max(word_count, 1)
    
    cognitive_load = min(10.0, (filler_count * 0.4) + (hedging_count * 0.6) + (repetition_ratio * 8.0))
    
    # Confidence Score (0-100)
    base_confidence = 88.0
    confidence_penalty = (filler_ratio * 120.0) + (hedge_ratio * 150.0)
    confidence_bonus = min(12.0, structural_count * 3.0)
    confidence_score = max(30.0, min(100.0, base_confidence - confidence_penalty + confidence_bonus))

    feedback_notes = []
    if filler_count > 3:
        feedback_notes.append(f"Reduce verbal fillers (detected {filler_count} instances like 'um/like/basically').")
    if hedging_count > 2:
        feedback_notes.append(f"State engineering decisions with conviction (replace '{list(HEDGING_WORDS)[0]}' with direct assertions).")
    if structural_count >= 2:
        feedback_notes.append("Excellent structured delivery with clear sequence markers.")

    return {
        "filler_count": filler_count,
        "hedging_count": hedging_count,
        "structural_markers_count": structural_count,
        "cognitive_load_score": round(cognitive_load, 2),
        "confidence_score": round(confidence_score, 1),
        "tone_clarity": "EXCELLENT" if confidence_score >= 85 else ("GOOD" if confidence_score >= 70 else "NEEDS_PRACTICE"),
        "feedback_notes": feedback_notes
    }

