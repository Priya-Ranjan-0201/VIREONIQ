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

import re

STAR_INDICATORS = {
    "situation": ["when", "project", "client", "problem", "incident", "outage", "legacy", "challenge", "context", "background", "stakeholder", "architecture", "scenario"],
    "task": ["my role", "responsible for", "assigned", "goal", "objective", "tasked with", "needed to", "mandate", "scope", "deliverable", "requirement", "target"],
    "action": ["i designed", "i implemented", "i built", "i refactored", "i investigated", "i led", "i wrote", "i configured", "i architected", "i orchestrated", "i optimized", "i debugged", "i deployed", "i spearheaded"],
    "result": ["result", "reduced", "improved", "increased", "achieved", "delivered", "%", "latency dropped", "saved", "scaled", "revenue", "uptime", "p99", "users", "throughput"],
    "reflection": ["learned", "retrospective", "post-mortem", "safeguard", "prevent", "in hindsight", "next time", "takeaway", "tradeoff", "mentored", "safeguards", "best practice"]
}

def evaluate_behavioral_response(
    question_prompt: str,
    response_text: str,
    response_duration_seconds: float = 45.0
) -> Dict[str, Any]:
    """
    Evaluates behavioral response against STAR+R criteria, computes communication proxies,
    and analyzes ownership and quantitative impact density.
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
                "hedging_density": 0.0,
                "ownership_ratio": 0.5
            },
            "confidence": "LOW",
            "reasoning": "Response too brief to assess behavioral competencies.",
            "strengths": [],
            "improvements": ["Provide a detailed STAR structured example with Situation, Task, Action, and Result."]
        }

    # 1. STAR Scores
    star_scores = {}
    present_elements = []
    missing_elements = []

    for dim, keywords in STAR_INDICATORS.items():
        hits = sum(1 for kw in keywords if kw in text_lower)
        score = min(100.0, 50.0 + (hits * 16.0))
        star_scores[dim] = round(score, 1)
        
        dim_label = dim.title()
        if hits >= 2:
            present_elements.append(f"Clear {dim_label} articulation.")
        elif hits == 0:
            missing_elements.append(f"Could strengthen {dim_label} quantification or details.")

    # 2. Metric & Impact Quantification Bonus
    metric_regex = r"(\d+(?:\.\d+)?%|\$\d+(?:,\d+)*(?:\.\d+)?|\b\d+x\b|\d+\+?\s*(?:users|requests|ms|s|events|queries|nodes|clients|rps|tps|lpa|stars)|\bthroughput\b|\blatency\b|\bavailability\b)"
    metrics_found = len(re.findall(metric_regex, text_lower))
    if metrics_found > 0:
        star_scores["result"] = min(100.0, star_scores["result"] + (min(metrics_found, 3) * 5.0))

    # 3. Overall Score Synthesis
    overall_score = round(
        (star_scores["situation"] * 0.15) +
        (star_scores["task"] * 0.15) +
        (star_scores["action"] * 0.35) +
        (star_scores["result"] * 0.25) +
        (star_scores["reflection"] * 0.10),
        1
    )

    # 4. Communication & Ownership Indicators
    duration_min = max(0.2, response_duration_seconds / 60.0)
    wpm = min(220.0, max(60.0, word_count / duration_min))
    
    # Ownership: I vs We count
    i_count = len(re.findall(r"\bi\b", text_lower))
    we_count = len(re.findall(r"\bwe\b", text_lower))
    ownership_ratio = round(i_count / max(i_count + we_count, 1), 2)

    hedges = sum(1 for h in ["maybe", "i guess", "probably", "sort of", "kind of", "i think", "somewhat", "perhaps"] if h in text_lower)
    hedging_density = round(hedges / max(word_count, 1), 3)

    return {
        "overall_score": overall_score,
        "star_scores": star_scores,
        "communication_indicators": {
            "word_count": word_count,
            "estimated_wpm": round(wpm, 1),
            "hedging_density": hedging_density,
            "ownership_ratio": ownership_ratio,
            "metrics_detected": metrics_found,
            "structure_signal": "STRONG" if len(present_elements) >= 3 else "MODERATE"
        },
        "confidence": "HIGH" if word_count >= 100 else "MEDIUM",
        "reasoning": f"STAR evaluation yielded {overall_score:.0f}/100 with clear action, result, and ownership articulation.",
        "strengths": present_elements[:3] if present_elements else ["Clear foundational communication"],
        "improvements": missing_elements[:2] if missing_elements else ["Add specific percentage-based business impact metrics"]
    }

