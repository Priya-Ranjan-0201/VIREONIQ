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
                "focus": "Architecture, Code Quality, Edge Cases",
                "rubric": "Look for depth in system design and awareness of failure modes."
            },
            {
                "role": "CultureSync", 
                "focus": "Communication, Ownership, Leadership",
                "rubric": "Evaluate if the candidate uses 'I' vs 'We' appropriately and takes ownership of failures."
            },
            {
                "role": "ProductThinker", 
                "focus": "User Impact, Product Logic, Practicality",
                "rubric": "Check if the technical solution serves the business goal or is over-engineered."
            }
        ]

    async def evaluate_response(self, question: str, answer: str, context: Dict = None) -> Dict:
        """
        Simulates a collaborative evaluation by all agents in the committee.
        """
        print(f"[Intelligence] Hiring Committee assembling for persona: {self.persona_name}")
        
        # Each agent evaluates based on their specific focus
        # In a real production deployment, these would run in parallel via an LLM API
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
            "hiring_consensus": self._get_consensus_label(avg_score)
        }

    async def _run_agent_inference(self, agent: Dict, question: str, answer: str, context: Dict) -> Dict:
        """
        Queries the LLM provider to evaluate the candidate's transcript from the perspective of this specific agent.
        """
        from core.llm.factory import get_llm_provider
        
        target_role = (context or {}).get("target_role", "Software Engineer")
        
        prompt = f"""
        You are an AI Hiring Agent evaluating an interview transcript for the role of '{target_role}'.
        
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
        ownership_keywords = ["optimized", "designed", "owned", "resolved", "metrics", "latency"]
        matches = sum(1 for word in ownership_keywords if word in answer.lower())
        
        if agent["role"] == "TechBarRaiser":
            score = 0.6 + (matches * 0.1)
            feedback = "Strong technical grounding." if matches > 2 else "Lacks specific technical depth."
        elif agent["role"] == "CultureSync":
            score = 0.7 if "i " in answer.lower() or "we " in answer.lower() else 0.5
            feedback = "Demonstrates good collaboration/ownership language."
        else:
            score = 0.65
            feedback = "Practical approach to the problem."

        return {
            "agent": agent["role"],
            "score": min(score, 1.0),
            "focus_feedback": feedback,
            "reasoning": f"Based on the focus on {agent['focus']}, the agent noted specific keywords and structure (Fallback Heuristics)."
        }

    def _generate_committee_debrief(self, evaluations: List[Dict]) -> str:
        """
        Synthesizes a short debrief narrative.
        """
        scores = [e["score"] for e in evaluations]
        if all(s > 0.8 for s in scores):
            return "The committee is unanimous: this is a bar-raising candidate."
        elif any(s < 0.5 for s in scores):
            weak_agent = next(e["agent"] for e in evaluations if e["score"] < 0.5)
            return f"The committee has concerns, specifically from the {weak_agent} perspective."
        return "A solid candidate with minor areas for improvement."

    def _get_consensus_label(self, score: float) -> str:
        if score >= 0.85: return "Strong Hire"
        if score >= 0.70: return "Hire"
        if score >= 0.50: return "Lean Hire"
        return "No Hire"

