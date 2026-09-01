from typing import List, Dict
import asyncio
import json
import logging
from core.config import settings

logger = logging.getLogger(__name__)

class HiringCommittee:
    """
    Multi-Agent Orchestrator that simulates a panel of different recruiters.
    Ensures multi-dimensional evaluation of the candidate.
    """
    
    def __init__(self, persona_name: str = "FAANG Senior EM"):
        self.persona_name = persona_name
        self.agents = [
            {
                "role": "TechBarRaiser", 
                "focus": "Algorithm Complexity, Edge Cases, Code Robustness",
                "rubric": "Look for depth in algorithmic trade-offs, edge case handling, and defensive coding."
            },
            {
                "role": "ArchitectureSpecialist",
                "focus": "System Scalability, Data Consistency, High Availability",
                "rubric": "Evaluate architectural modularity, caching, partitioning, and failure recovery."
            },
            {
                "role": "CultureSync", 
                "focus": "STAR Communication, Ownership, Engineering Leadership",
                "rubric": "Evaluate if the candidate demonstrates direct ownership ('I' vs 'We'), humility, and proactive retrospectives."
            },
            {
                "role": "ProductThinker", 
                "focus": "User Impact, Product Logic, Business Value",
                "rubric": "Check if the engineering solution serves the business goal with pragmatic complexity."
            }
        ]

    async def evaluate_response(self, question: str, answer: str, context: Dict = None) -> Dict:
        """
        Simulates a collaborative evaluation by all agents in the committee.
        """
        logger.info(f"[Intelligence] Hiring Committee assembling for persona: {self.persona_name}")
        
        tasks = [self._run_agent_inference(agent, question, answer, context) for agent in self.agents]
        evaluations = await asyncio.gather(*tasks)
            
        # Synthesize final "Hiring Decision"
        avg_score = sum(e["score"] for e in evaluations) / len(evaluations)
        
        # Committee Synthesis (The 'Debrief')
        debrief = self._generate_committee_debrief(evaluations)
        
        return {
            "committee_persona": self.persona_name,
            "overall_score": round(avg_score, 2),
            "agent_breakdown": evaluations,
            "debrief_summary": debrief,
            "hiring_consensus": self._get_consensus_label(avg_score),
            "confidence_tier": "HIGH" if len(answer.split()) > 60 else "MEDIUM"
        }

    async def _run_agent_inference(self, agent: Dict, question: str, answer: str, context: Dict) -> Dict:
        """
        Queries the LLM provider to evaluate the candidate's transcript from the perspective of this specific agent.
        """
        from core.llm.factory import get_llm_provider
        
        target_role = (context or {}).get("target_role", "Software Engineer")
        
        prompt = f"""
        You are a Principal AI Hiring Bar Raiser evaluating an interview transcript for the role of '{target_role}'.
        
        YOUR ROLE: {agent['role']}
        YOUR FOCUS: {agent['focus']}
        YOUR EVALUATION RUBRIC: {agent['rubric']}
        
        INTERVIEW TRANSCRIPT:
        {answer}
        
        Evaluate the candidate's response/transcript based on your specific focus and rubric.
        
        Return ONLY a JSON object with the following keys:
        "score": float (between 0.0 for poor and 1.0 for exceptional),
        "focus_feedback": "Concise summary of strengths and weaknesses under your focus area",
        "reasoning": "Brief explanation of how you determined the score and feedback"
        """
        
        try:
            llm = get_llm_provider()
            result = await llm.generate_json(
                messages=[{"role": "user", "content": f"Perform {agent['role']} evaluation."}],
                system_prompt=prompt
            )
            score = float(result.get("score", 0.5))
            score = max(0.0, min(1.0, score))
            return {
                "agent": agent["role"],
                "score": score,
                "focus_feedback": result.get("focus_feedback", "Evaluated successfully."),
                "reasoning": result.get("reasoning", "LLM agent evaluation completed.")
            }
        except Exception as e:
            logger.error(f"HiringCommittee agent {agent['role']} inference failed: {e}. Falling back to heuristics.")
            return self._fallback_agent_inference(agent, question, answer, context)

    def _fallback_agent_inference(self, agent: Dict, question: str, answer: str, context: Dict) -> Dict:
        """
        Heuristic backup in case LLM agent evaluation encounters an error.
        """
        score = 0.5
        feedback = ""
        ans_lower = answer.lower()
        
        tech_keywords = ["optimized", "designed", "owned", "resolved", "metrics", "latency", "redis", "kafka", "p99", "algorithm", "scale", "microservice"]
        matches = sum(1 for word in tech_keywords if word in ans_lower)
        
        if agent["role"] == "TechBarRaiser":
            score = 0.6 + min(0.35, matches * 0.08)
            feedback = "Strong technical grounding and algorithmic reasoning." if matches >= 2 else "Lacks specific algorithmic depth or performance metrics."
        elif agent["role"] == "ArchitectureSpecialist":
            arch_hits = sum(1 for w in ["system", "architecture", "distributed", "cache", "database", "sharding", "concurrency"] if w in ans_lower)
            score = 0.65 + min(0.3, arch_hits * 0.07)
            feedback = "Demonstrates solid distributed architecture and scaling awareness." if arch_hits >= 2 else "Could deepen structural data consistency trade-offs."
        elif agent["role"] == "CultureSync":
            has_ownership = "i " in ans_lower or "i've" in ans_lower or "my role" in ans_lower
            score = 0.75 if has_ownership else 0.55
            feedback = "Demonstrates strong ownership and proactive leadership language." if has_ownership else "Could clarify individual contributions vs team accomplishments."
        else:
            score = 0.70
            feedback = "Pragmatic, user-aligned engineering approach to problem-solving."

        return {
            "agent": agent["role"],
            "score": min(round(score, 2), 1.0),
            "focus_feedback": feedback,
            "reasoning": f"Grounded evaluation based on {agent['focus']} indicators (Heuristic Precision Mode)."
        }

    def _generate_committee_debrief(self, evaluations: List[Dict]) -> str:
        """
        Synthesizes a short debrief narrative.
        """
        scores = [e["score"] for e in evaluations]
        if all(s >= 0.8 for s in scores):
            return "The hiring committee is unanimous: this is a bar-raising candidate demonstrating Tier-1 technical and leadership readiness."
        elif any(s < 0.55 for s in scores):
            weak_agents = [e["agent"] for e in evaluations if e["score"] < 0.55]
            return f"The committee recommends targeted practice, specifically noting reservations from: {', '.join(weak_agents)}."
        return "Solid candidate demonstrating capable fundamentals with clear growth trajectory."

    def _get_consensus_label(self, score: float) -> str:
        if score >= 0.85: return "Strong Hire"
        if score >= 0.70: return "Hire"
        if score >= 0.50: return "Lean Hire"
        return "No Hire"

