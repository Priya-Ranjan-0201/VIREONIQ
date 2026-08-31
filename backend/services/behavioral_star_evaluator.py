"""
Behavioral STAR Evaluator & Communication Indicator Engine.
Evaluates structured behavioral interview responses using the STAR framework:
  - Situation: Context and problem description
  - Task: Candidate's direct role and ownership
  - Action: Specific, actionable technical/leadership steps taken
  - Result: Quantifiable business or technical outcome
  - Reflection: Lessons learned and preventative safeguards
Also extracts observable communication indicators (structure markers, pace, hedging).
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

STAR_INDICATORS = {
    "situation": ["when", "project", "client", "problem", "incident", "outage", "legacy", "challenge"],
    "task": ["my role", "responsible for", "assigned", "goal", "objective", "tasked with", "needed to"],
    "action": ["i designed", "i implemented", "i built", "i refactored", "i investigated", "i led", "i wrote", "i configured"],
    "result": ["result", "reduced", "improved", "increased", "achieved", "delivered", "%", "latency dropped", "saved"],
    "reflection": ["learned", "retrospective", "post-mortem", "safeguard", "prevent", "in hindsight", "next time"]
}

def evaluate_behavioral_response(
    question_prompt: str,
    response_text: str,
    response_duration_seconds: float = 45.0
) -> Dict[str, Any]:
    """
    Evaluates behavioral response against STAR criteria and computes communication proxies.
    """
    text_lower = response_text.lower()
    words = response_text.split()
    word_count = len(words)

    if word_count < 25:
        return {
            "overall_score": 40.0,
            "star_scores": {k: 35.0 for k in STAR_INDICATORS},
            "communication_indicators": {
                "word_count": word_count,
                "structure_clarity": "POOR",
                "hedging_density": 0.0
            },
            "confidence": "LOW",
            "reasoning": "Response too brief to assess behavioral competencies.",
            "strengths": [],
            "improvements": ["Provide a detailed STAR structured example"]
        }

    # 1. STAR Scores
    star_scores = {}
    present_elements = []
    missing_elements = []

    for dim, keywords in STAR_INDICATORS.items():
        hits = sum(1 for kw in keywords if kw in text_lower)
        score = min(100.0, 50.0 + (hits * 18.0))
        star_scores[dim] = round(score, 1)
        
        dim_label = dim.title()
        if hits >= 2:
            present_elements.append(f"Clear {dim_label} articulation.")
        elif hits == 0:
            missing_elements.append(f"Could strengthen {dim_label} quantification or details.")

    # 2. Overall Score
    overall_score = round(
        (star_scores["situation"] * 0.15) +
        (star_scores["task"] * 0.15) +
        (star_scores["action"] * 0.35) +
        (star_scores["result"] * 0.25) +
        (star_scores["reflection"] * 0.10),
        1
    )

    # 3. Communication indicators
    duration_min = max(0.2, response_duration_seconds / 60.0)
    wpm = min(220.0, max(60.0, word_count / duration_min))
    hedges = sum(1 for h in ["maybe", "i guess", "probably", "sort of", "kind of", "i think"] if h in text_lower)
    hedging_density = round(hedges / max(word_count, 1), 3)

    return {
        "overall_score": overall_score,
        "star_scores": star_scores,
        "communication_indicators": {
            "word_count": word_count,
            "estimated_wpm": round(wpm, 1),
            "hedging_density": hedging_density,
            "structure_signal": "STRONG" if len(present_elements) >= 3 else "MODERATE"
        },
        "confidence": "HIGH" if word_count >= 100 else "MEDIUM",
        "reasoning": f"STAR evaluation yielded {overall_score:.0f}/100 with clear action and result components.",
        "strengths": present_elements[:3] if present_elements else ["Good clarity of thought"],
        "improvements": missing_elements[:2] if missing_elements else ["Add specific percentage-based business impact metrics"]
    }
