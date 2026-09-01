import json
import logging
from typing import List, Dict, Any, Optional
from core.llm.base import BaseLLMProvider

logger = logging.getLogger(__name__)

QUESTIONS_MAP = {
    "coding": [
        "Welcome to the coding simulator. Let's start with a classic system design and algorithmic challenge. Could you describe how you would design a rate limiter for a high-traffic microservices architecture? What data structures and algorithms would you use to track request limits, and how would you handle distributed state?",
        "That's a solid start. Let's drill into the implementation. How would you handle race conditions when updating request counts in a distributed system like Redis? What are the trade-offs between Token Bucket and Leaking Bucket algorithms for this use case?",
        "Excellent. Let's write some code to represent this. How would you implement a simple in-memory Token Bucket rate limiter in Python/JS, ensuring thread safety? Walk me through your design and locking mechanism.",
        "Good. Now let's discuss edge cases. What happens if a user floods the rate limiter with a burst of requests exactly at the boundary of a window in a Fixed Window counter? How does Sliding Window Log address this, and what is the storage overhead?",
        "Thank you. I have all the signals I need. Let's conclude this session and review your performance scorecard. Feel free to ask any final questions."
    ],
    "cybersecurity": [
        "Welcome to the Cybersecurity Specialist simulation. Let's begin. Imagine you discover an unauthorized active SSH session on a critical database server during a routine audit. Walk me through your immediate incident response steps to contain and analyze this potential breach.",
        "Containment is crucial. Now, how would you proceed with identifying the root cause? What logs, files, and network telemetry would you examine to determine if data was exfiltrated, and how would you preserve chain of custody for evidence?",
        "Let's talk network security. How would you configure a zero-trust network access (ZTNA) architecture to prevent this type of lateral movement in the future? What role do IAM policies and network segmentation play here?",
        "Interesting. If the attacker used a zero-day exploit to gain access, how would your endpoint detection and response (EDR) system identify anomalous behavior without a known signature?",
        "Thank you for the detailed walkthrough. The security committee has enough information. Let's finalize the assessment."
    ],
    "technical": [
        "Welcome to the Technical Interview simulation. Let's begin by discussing a recent complex technical project you spearheaded. Can you explain the system architecture, the primary challenges you faced, and how you made the core technology decisions?",
        "That sounds like a substantial project. Let's dive deeper into the architecture. How did you design for scale, and how did you handle data consistency and latency issues across different services?",
        "Let's talk about performance optimization. If you noticed a sudden spike in latency on your read operations under heavy load, what diagnostic steps would you take, and how would caching or indexing strategies be applied?",
        "Great. Now, let's discuss collaboration and code quality. How do you balance delivering features quickly with maintaining a clean, well-tested codebase? Can you share your approach to code reviews and mentoring?",
        "Thank you. That completes our technical evaluation. I will compile the feedback from the committee now."
    ]
}

DEFAULT_FOLLOWUPS = [
    "That makes sense. Can you explain the key tradeoffs of this approach compared to other industry alternatives?",
    "Could you elaborate more on how you handled scalability and error-handling in that scenario?",
    "How would you monitor and observe this system in a production environment to detect anomalies early?",
    "If you had to build this again from scratch with unlimited budget, what architectural changes would you make?",
]

class MockLLMProvider(BaseLLMProvider):
    async def chat(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
        # Determine track
        track = "technical"
        combined_prompts = (system_prompt or "") + " " + " ".join([m.get("content", "") for m in messages])
        combined_prompts_lower = combined_prompts.lower()
        if "cybersecurity" in combined_prompts_lower or "security" in combined_prompts_lower:
            track = "cybersecurity"
        elif "coding" in combined_prompts_lower or "code" in combined_prompts_lower:
            track = "coding"

        # Count how many assistant turns are in messages
        assistant_msgs = [m for m in messages if m.get("role") == "assistant"]
        
        # Check if the last user message was a start command
        user_msgs = [m for m in messages if m.get("role") == "user"]
        is_starting = len(user_msgs) == 1 and "start" in user_msgs[0].get("content", "").lower()
        
        if is_starting:
            turn_idx = 0
        else:
            turn_idx = len(assistant_msgs)

        questions = QUESTIONS_MAP[track]
        if turn_idx < len(questions):
            return questions[turn_idx]
        else:
            followup_idx = (turn_idx - len(questions)) % len(DEFAULT_FOLLOWUPS)
            return DEFAULT_FOLLOWUPS[followup_idx]

    async def generate_json(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> Dict[str, Any]:
        system_prompt_lower = (system_prompt or "").lower()
        combined_text = (system_prompt_lower + " " + " ".join([m.get("content", "") for m in messages])).lower()

        # ─── Resume Builder / MNC Optimization Mock Handlers ──────────────────
        if "parse" in combined_text and ("resume" in combined_text or "extract" in combined_text):
            from services.resume_builder_service import _heuristic_parse_resume
            content = " ".join([m.get("content", "") for m in messages])
            if "Raw Resume Text:" in content:
                raw_text = content.split("Raw Resume Text:", 1)[1].split("Target Role:", 1)[0].strip()
            else:
                raw_text = content
            return _heuristic_parse_resume(raw_text, "Software Engineer")

        if "optimize" in combined_text or "mnc" in combined_text or "boost" in combined_text or "generate" in combined_text:
            from services.resume_builder_service import _rule_based_mnc_optimizer
            import re
            content = " ".join([m.get("content", "") for m in messages])
            resume_dict = {}
            target_role = "Full Stack Software Engineer"
            target_company = "Google"

            role_match = re.search(r'for (?:the )?role:\s*([^\(\n]+)', content, re.IGNORECASE)
            if role_match:
                target_role = role_match.group(1).strip()

            comp_match = re.search(r'Target Tier:\s*([^\)\n]+)', content, re.IGNORECASE)
            if comp_match:
                target_company = comp_match.group(1).strip()

            if "Input Resume Data:" in content:
                raw_data = content.split("Input Resume Data:", 1)[1].split("Transformation Rules:", 1)[0].strip()
                try:
                    import ast
                    resume_dict = ast.literal_eval(raw_data)
                except Exception:
                    pass
            return _rule_based_mnc_optimizer(resume_dict, target_role, target_company)

        if "improve" in combined_text or "section" in combined_text:
            return {
                "improved_content": "Architected and delivered distributed microservice architecture utilizing Python FastAPI and Redis caching, reducing p99 API response latency by 45% across 10M+ daily requests while achieving 99.99% system availability.",
                "changes_made": [
                    "Applied Google XYZ impact structure (Accomplished [X] measured by [Y] doing [Z])",
                    "Replaced passive voice with strong Tier-1 action verbs ('Architected and delivered')",
                    "Added verified quantitative metric ('45% latency reduction across 10M+ daily requests')"
                ],
                "ats_keywords_added": ["Distributed Microservices", "FastAPI", "Redis Caching", "High-Throughput", "p99 Latency"]
            }

        # ─── System Design Architecture Mock Handler ─────────────────────────
        if "system design" in combined_text or "architecture" in combined_text and "criteria" in combined_text:
            from services.system_design_evaluator import evaluate_system_design_response
            content = " ".join([m.get("content", "") for m in messages])
            return evaluate_system_design_response("Design a scalable distributed system", content)

        # ─── Behavioral STAR Evaluation Mock Handler ──────────────────────────
        if "behavioral" in combined_text or "star" in combined_text and "situation" in combined_text:
            from services.behavioral_star_evaluator import evaluate_behavioral_response
            content = " ".join([m.get("content", "") for m in messages])
            return evaluate_behavioral_response("Describe a challenging technical situation", content)

        # ─── Hiring Committee Agent Mock Handler ─────────────────────────────
        if "hiring agent" in combined_text or "techbarraiser" in combined_text or "culturesync" in combined_text:
            return {
                "score": 0.88,
                "focus_feedback": "Candidate articulated clear architectural trade-offs, defensive error boundaries, and quantitative impact.",
                "reasoning": "Demonstrated high technical ownership and awareness of failure modes in distributed environments."
            }

        # ─── Gap Analysis Mock Handler ────────────────────────────────────────
        if "5-dimensional gap analysis" in combined_text or "gap_analysis" in combined_text:
            return {
                "technical_gap_score": 82.0,
                "communication_gap_score": 88.0,
                "project_gap_score": 78.0,
                "confidence_gap_score": 85.0,
                "consistency_gap_score": 90.0,
                "overall_readiness_score": 84.6,
                "missing_skills": ["Distributed Caching", "Idempotency"],
                "placement_probability": 86.5,
                "recommendations": [
                    {
                        "time_horizon_days": 30,
                        "dimension": "technical",
                        "task_description": "Implement an end-to-end Redis cache-aside microservice with exponential backoff retries.",
                        "resources": ["https://redis.io/docs/manual/patterns/distributed-locks/"]
                    }
                ]
            }

        if "feedback" in combined_text:
            return {
                "overall_score": 94,
                "section_scores": {
                    "summary": 92,
                    "experience": 96,
                    "education": 95,
                    "skills": 94,
                    "projects": 93
                },
                "strengths": [
                    "Exceptional quantification in experience bullet points with clear business impact.",
                    "High density of Tier-1 leadership action verbs (Architected, Spearheaded, Engineered).",
                    "Strong alignment with Fortune 500 tech stack requirements."
                ],
                "weaknesses": [
                    "Could highlight cloud cost optimization or scalability metrics in project descriptions."
                ],
                "missing_keywords": ["System Design", "Distributed Systems", "CI/CD Pipelines", "Observability"],
                "action_items": [
                    "Incorporate 'System Design' in the technical skills cloud section.",
                    "Ensure all metrics feature measurable outcomes (%, $, latency, or scale)."
                ]
            }

        # ─── Default Technical Interview JSON Simulation ──────────────────────
        # Check if the question is concluding
        is_concluding = False
        concluding_phrases = [
            "conclude this session",
            "finalize the assessment",
            "compile the feedback"
        ]
        for phrase in concluding_phrases:
            if phrase in system_prompt_lower:
                is_concluding = True
                break

        # Parse or default values
        technical_score = 85.0
        clarity_score = 90.0
        confidence_score = 88.0
        completeness_score = 85.0
        
        # Extract user answer from system prompt
        user_answer = ""
        if "candidate answer:" in system_prompt_lower:
            parts = system_prompt.split("CANDIDATE ANSWER:")
            if len(parts) > 1:
                user_answer = parts[1].split("QUESTION ASKED:")[0].strip()

        word_count = len(user_answer.split())
        
        if word_count < 10:
            technical_score = 52.0
            clarity_score = 60.0
            confidence_score = 55.0
            completeness_score = 45.0
            feedback = "Your answer was too brief. Try using the STAR methodology (Situation, Task, Action, Result) and expanding on technical trade-offs."
            correctness_level = "correct_but_shallow"
        elif word_count < 30:
            technical_score = 74.0
            clarity_score = 82.0
            confidence_score = 78.0
            completeness_score = 70.0
            feedback = "Solid answer, but you can build greater credibility by mentioning metrics and highlighting your direct actions."
            correctness_level = "partial_answer"
        else:
            bonus_points = min(12.0, (word_count - 30) * 0.15)
            technical_score = 85.0 + bonus_points
            clarity_score = 90.0
            confidence_score = 86.0
            completeness_score = 85.0 + bonus_points
            feedback = "Excellent depth and structure. You hit key architecture elements and demonstrated ownership of the system."
            correctness_level = "correct_all_keypoints"
            
        bonuses = ["used_correct_terminology", "gave_concrete_example"]
        if word_count > 45:
            bonuses.append("structured_answer_star_format")
            bonuses.append("mentioned_trade_offs")
            
        penalties = []
        if word_count < 8:
            penalties.append("answer_abandoned_midway")

        return {
            "correctness_level": correctness_level,
            "bonuses_earned": bonuses,
            "penalties_incurred": penalties,
            "technical_correctness": round(technical_score, 1),
            "communication_clarity": round(clarity_score, 1),
            "confidence_tone": round(confidence_score, 1),
            "completeness": round(completeness_score, 1),
            "feedback_for_user": feedback,
            "next_action": "generate_deeper_follow_up" if not is_concluding else "explain_then_test",
            "is_concluding": is_concluding
        }
