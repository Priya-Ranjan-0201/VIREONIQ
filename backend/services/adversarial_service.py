"""
Adversarial Interviewer service.
Simulates high-pressure, hostile interview tactics and evaluates student composure and resilience.
"""

import logging
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from core.llm.nvidia import NVIDIA_NIM_Client
from core.config import settings

logger = logging.getLogger(__name__)

TACTIC_TEMPLATES = {
    "mid_answer_interrupt": "Stop. You just said '{claim}'. Why '{claim}' and not '{alternative}'? Defend your choice right now.",
    "challenge_correct": "That's the textbook answer. Every candidate says exactly that. What would a senior engineer know that you have not mentioned?",
    "feign_confusion": "I am completely lost. Start over with a completely different analogy. Pretend I have never heard of this.",
    "rapid_fire": "Answer these four questions quickly: 1) What is the time complexity? 2) How do you scale it? 3) What is the single point of failure? 4) How do you monitor it? Go.",
    "bluff_challenge": "But {wrong_claim} is actually better in this case, is it not?"
}

@dataclass
class AdversarialResponse:
    tactic: Optional[str]
    interviewer_statement: str
    tactic_usage: dict
    is_adversarial: bool

async def run_adversarial_session(
    session_id: str,
    exchange_number: int,
    student_answer: str,
    confidence_estimate: float, # Composure score source
    evaluation_strength: str, # 'strong', 'partial', 'evasive'
    session_state: dict,
    anthropic_client = None
) -> AdversarialResponse:
    """
    Selects a stress-tactic based on answer evaluation metrics and returns the hostile prompt.
    """
    tactic_usage = session_state.get("tactic_usage", {})
    composure_scores = session_state.get("composure_scores", [])

    # Limit total tactic uses per session to 3
    total_used = sum(tactic_usage.values())
    if total_used >= 3:
        return AdversarialResponse(tactic=None, interviewer_statement="", tactic_usage=tactic_usage, is_adversarial=False)

    # 1. Select Tactic
    available = [t for t in TACTIC_TEMPLATES.keys() if tactic_usage.get(t, 0) < 1]
    if not available:
         return AdversarialResponse(tactic=None, interviewer_statement="", tactic_usage=tactic_usage, is_adversarial=False)

    if evaluation_strength == "strong" and "challenge_correct" in available:
        tactic = "challenge_correct"
    elif evaluation_strength in ("partial", "evasive") and "feign_confusion" in available:
        tactic = "feign_confusion"
    elif exchange_number % 4 == 0 and "rapid_fire" in available:
        tactic = "rapid_fire"
    else:
        tactic = random.choice(available)

    # Hydrate Tactic details
    claim = "this is the optimal approach"
    alternative = "an alternative event-driven pattern"
    wrong_claim = "using a global lock"
    
    # Simple extraction from student answer for realism
    words = student_answer.split()
    if len(words) > 3:
        claim = " ".join(words[:4])
        
    template = TACTIC_TEMPLATES[tactic].format(
        claim=claim,
        alternative=alternative,
        wrong_claim=wrong_claim
    )

    prompt = f"""
    You are a hostile, high-pressure interviewer executing the '{tactic}' interview tactic.
    The candidate just said: '{student_answer[:400]}'
    Generate the adversarial interviewer response using this exact tactic template concept:
    "{template}"
    
    Guidelines:
    - Be extremely challenging and critical, but remain strictly professional. Never be personally insulting.
    - If bluff_challenge is selected, present the technically incorrect claim '{wrong_claim}' as if it is obviously correct to test if the candidate has the confidence to respectfully disagree.
    
    Return ONLY the interviewer's direct statement, no explanations.
    """

    try:
        if settings.ANTHROPIC_API_KEY:
            from anthropic import Anthropic
            client = anthropic_client or Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            resp = client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            interviewer_statement = resp.content[0].text.strip()
        else:
            client = NVIDIA_NIM_Client()
            interviewer_statement = await client.generate(prompt)
    except Exception as e:
        logger.error(f"Adversarial LLM query failed: {e}")
        interviewer_statement = template

    # Record composure score before this event (confidence_estimate ranges 0.0 - 1.0)
    composure_before = confidence_estimate * 100.0
    composure_scores.append(composure_before)
    
    # Increment tactic usage
    tactic_usage[tactic] = tactic_usage.get(tactic, 0) + 1
    session_state["tactic_usage"] = tactic_usage
    session_state["composure_scores"] = composure_scores

    return AdversarialResponse(
        tactic=tactic,
        interviewer_statement=interviewer_statement,
        tactic_usage=tactic_usage,
        is_adversarial=True
    )

async def generate_adversarial_debrief(
    session_id: str,
    tactic_log: List[dict],  # list of {"tactic": str, "composure_before": float, "composure_after": float}
    composure_log: List[float],
    anthropic_client = None
) -> dict:
    """
    Analyzes composure drop across tactics and generates a supportive post-adversarial debrief.
    """
    logger.info(f"Generating adversarial debrief for session_id={session_id}")
    
    worst_tactic = "none"
    max_drop = 0.0
    before_val = 100.0
    after_val = 100.0

    for log in tactic_log:
        before = log.get("composure_before", 100.0)
        after = log.get("composure_after", 100.0)
        drop = before - after
        if drop > max_drop:
            max_drop = drop
            worst_tactic = log.get("tactic", "unknown")
            before_val = before
            after_val = after

    # Calculate overall pressure resistance score
    avg_composure = sum(composure_log) / len(composure_log) if composure_log else 80.0
    pressure_resistance_score = int(max(0.0, min(100.0, avg_composure - (max_drop * 0.5))))

    prompt = f"""
    Generate a supportive post-adversarial interview debrief.
    - Composure Drop: The tactic '{worst_tactic}' caused candidate composure to drop from {before_val:.1f}% to {after_val:.1f}%.
    - Composure Trajectory across session: {composure_log}
    
    Generate JSON response with these keys:
    1. "pressure_resistance_score": {pressure_resistance_score},
    2. "recovery_techniques": ["technique 1", "technique 2"] (how to stay calm under this specific tactic '{worst_tactic}'),
    3. "what_to_say_next_time": f"Specific script template for replying to the {worst_tactic} tactic professionally.",
    4. "overall_assessment": "Two supportive sentences summarizing their resilience."
    """

    try:
        if settings.ANTHROPIC_API_KEY:
            from anthropic import Anthropic
            client = anthropic_client or Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            resp = client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            raw_content = resp.content[0].text
        else:
            client = NVIDIA_NIM_Client()
            raw_content = await client.generate(prompt)

        import json
        import re
        match = re.search(r"\{.*\}", raw_content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        logger.error(f"Failed to generate adversarial debrief LLM: {e}")

    return {
        "pressure_resistance_score": pressure_resistance_score,
        "recovery_techniques": ["Take a deep breath and pause before replying", "Acknowledge the interviewer's perspective to buy time"],
        "what_to_say_next_time": "That is a valid concern. Let me break down my trade-off choices to show why I chose this path.",
        "overall_assessment": "You maintained a solid baseline of confidence. Under pressure, focusing on structure will help keep your answers grounded."
    }
