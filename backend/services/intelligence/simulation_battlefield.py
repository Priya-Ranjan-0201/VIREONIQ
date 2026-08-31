from typing import Dict, List, Any
import random
import uuid

class SimulationBattlefield:
    """
    Enterprise-Specific Interview Battlefield Simulator.
    
    Generates fully contextual scenarios based on target company DNA.
    Unlike the generic DynamicQuestionEngine, this produces scenarios
    that mirror the exact type of problems encountered at specific firms.
    """
    
    COMPANY_SCENARIOS = {
        "Google": {
            "culture": "Innovation-first, data-driven, scale-obsessed",
            "stages": [
                {
                    "stage": "Phone Screen",
                    "scenario": "Design a URL shortener that handles 1B requests/day. The interviewer will probe on hash collision, caching, and analytics.",
                    "eval_focus": ["System Design", "Scale Thinking", "Trade-off Analysis"],
                    "time_limit_min": 35
                },
                {
                    "stage": "Onsite - Coding",
                    "scenario": "Given a stream of user events (click, scroll, hover), implement a real-time anomaly detector that flags bot traffic with O(1) amortized space.",
                    "eval_focus": ["Algorithms", "Edge Cases", "Code Quality"],
                    "time_limit_min": 45
                },
                {
                    "stage": "Onsite - Behavioral",
                    "scenario": "Tell me about a time you had to push back on a senior engineer's design decision. What data did you use to support your position?",
                    "eval_focus": ["Ownership", "Communication", "Data-Driven"],
                    "time_limit_min": 20
                },
                {
                    "stage": "Bar Raiser",
                    "scenario": "Your team shipped a feature that caused a 2% drop in ad revenue across a major market. Walk me through your incident response, root cause analysis, and the post-mortem you would write.",
                    "eval_focus": ["Incident Response", "Leadership", "Accountability"],
                    "time_limit_min": 30
                }
            ]
        },
        "Amazon": {
            "culture": "Customer obsession, bias for action, ownership",
            "stages": [
                {
                    "stage": "OA - Leadership Principles",
                    "scenario": "Describe a situation where you had to make a decision with incomplete data. How did you mitigate the risks? Frame your answer using the STAR method and reference at least two Amazon Leadership Principles.",
                    "eval_focus": ["Bias for Action", "Ownership", "STAR Method"],
                    "time_limit_min": 25
                },
                {
                    "stage": "System Design",
                    "scenario": "Design the backend for Amazon's 'Customers who bought this also bought' recommendation engine. Consider cold-start problem, A/B testing framework, and real-time ingestion.",
                    "eval_focus": ["Architecture", "ML Systems", "Scale"],
                    "time_limit_min": 45
                },
                {
                    "stage": "Bar Raiser",
                    "scenario": "You discover that a critical microservice your team owns has been silently dropping 0.1% of transactions for the past 3 months. No customer complaints yet. What do you do?",
                    "eval_focus": ["Customer Obsession", "Integrity", "Deep Dive"],
                    "time_limit_min": 30
                }
            ]
        },
        "Startup": {
            "culture": "Speed, resourcefulness, full-stack ownership",
            "stages": [
                {
                    "stage": "Technical Deep Dive",
                    "scenario": "We have a monolithic {language} application serving 50K DAU. The CEO wants to ship a real-time collaboration feature in 2 weeks. How do you architect this without rewriting the entire backend?",
                    "eval_focus": ["Pragmatism", "Speed", "Architecture"],
                    "time_limit_min": 40
                },
                {
                    "stage": "Culture Fit",
                    "scenario": "Our last engineer quit because they felt micromanaged. How would you handle a situation where the founder gives you a vague spec and expects delivery by Friday?",
                    "eval_focus": ["Ambiguity Tolerance", "Communication", "Self-Direction"],
                    "time_limit_min": 20
                }
            ]
        }
    }

    def generate_simulation(self, company: str, stage_index: int = 0, user_context: Dict = None) -> Dict[str, Any]:
        """
        Generate a full simulation for a specific company and interview stage.
        """
        company_data = self.COMPANY_SCENARIOS.get(company)
        if not company_data:
            company_data = self.COMPANY_SCENARIOS["Startup"]
            company = "Startup"
        
        stages = company_data["stages"]
        stage = stages[min(stage_index, len(stages) - 1)]
        
        # Hydrate dynamic variables
        scenario_text = stage["scenario"].format(
            language=random.choice(["Python", "Go", "TypeScript", "Java"]),
            service=random.choice(["Auth", "Payments", "Notifications"]),
        )
        
        return {
            "id": str(uuid.uuid4()),
            "company": company,
            "company_culture": company_data["culture"],
            "stage": stage["stage"],
            "stage_number": stage_index + 1,
            "total_stages": len(stages),
            "scenario": scenario_text,
            "eval_focus": stage["eval_focus"],
            "time_limit_min": stage["time_limit_min"],
            "tips": self._generate_tips(company, stage["eval_focus"])
        }

    def get_available_companies(self) -> List[str]:
        return list(self.COMPANY_SCENARIOS.keys())

    def _generate_tips(self, company: str, eval_focus: List[str]) -> List[str]:
        tips = []
        if company == "Google":
            tips.append("Google values structured thinking. Always start with clarifying questions.")
        elif company == "Amazon":
            tips.append("Frame EVERY answer around a Leadership Principle. They score on it.")
        else:
            tips.append("Show you can ship fast. Mention specific timelines and trade-offs.")
        
        if "System Design" in eval_focus or "Architecture" in eval_focus:
            tips.append("Draw the high-level diagram first, then drill into the bottleneck.")
        if "Ownership" in eval_focus:
            tips.append("Use 'I' not 'We'. They want to hear YOUR contribution.")
            
        return tips
