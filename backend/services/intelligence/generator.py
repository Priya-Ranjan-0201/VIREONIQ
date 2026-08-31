from typing import List, Dict
import random
import uuid

class DynamicQuestionEngine:
    """
    Self-Evolving Question Generator.
    Generates 'Battlefield' scenarios that test real engineering ability.
    """
    
    SCENARIO_TEMPLATES = [
        {
            "id": "scenario_001",
            "type": "Broken Production",
            "scenario": "Your team just deployed a change to the {service} and the error rate spiked to 15%. Logs show {error_type}. How do you triage this?",
            "eval_focus": ["Debugging", "Incident Response", "Ownership"],
            "base_difficulty": 0.5
        },
        {
            "id": "scenario_002",
            "type": "Scaling Failure",
            "scenario": "The {db_type} database is hitting 95% CPU utilization during peak hours. You cannot upgrade the instance size. What architectural changes do you propose?",
            "eval_focus": ["Architecture", "System Design", "Cost-Efficiency"],
            "base_difficulty": 0.8
        },
        {
            "id": "scenario_003",
            "type": "Legacy Debt",
            "scenario": "You are tasked with replacing a critical {language} module written 5 years ago with no tests. How do you ensure zero-downtime migration?",
            "eval_focus": ["Pragmatism", "Risk Management", "Testing"],
            "base_difficulty": 0.7
        },
        {
            "id": "scenario_004",
            "type": "Security Breach",
            "scenario": "An audit reveals that a {service} is vulnerable to SQL injection due to an old {db_type} driver. It's production data. What's your immediate action?",
            "eval_focus": ["Security", "Urgency", "Communication"],
            "base_difficulty": 0.9
        }
    ]

    SERVICES = ["Payment Gateway", "Auth Service", "Matching Engine", "Notification Dispatcher", "Inventory Manager"]
    ERRORS = ["NullPointerException", "Connection Timeout", "OOM Kill", "Data Inconsistency", "Deadlock"]
    DBS = ["PostgreSQL", "Redis", "MongoDB", "Elasticsearch", "Cassandra"]

    def generate_battlefield_question(self, difficulty: float = 1.0, user_context: Dict = None) -> Dict:
        """
        Generates a completely new, non-memorizable engineering scenario.
        Adjusts selection based on desired difficulty.
        """
        # Filter templates by difficulty range
        suitable_templates = [
            t for t in self.SCENARIO_TEMPLATES 
            if (difficulty - 0.3) <= t["base_difficulty"] <= (difficulty + 0.3)
        ]
        
        if not suitable_templates:
            suitable_templates = self.SCENARIO_TEMPLATES

        template = random.choice(suitable_templates)
        
        # Hydrate template with dynamic variables
        question = template["scenario"].format(
            service=random.choice(self.SERVICES),
            error_type=random.choice(self.ERRORS),
            db_type=random.choice(self.DBS),
            language=random.choice(["Python", "Java", "Go", "TypeScript", "Rust"])
        )

        return {
            "id": str(uuid.uuid4()),
            "type": "battlefield",
            "category": template["type"],
            "question_text": question,
            "eval_focus": template["eval_focus"],
            "difficulty": template["base_difficulty"],
            "metadata": {
                "template_id": template["id"],
                "generated_at": "dynamic"
            }
        }

    def calculate_reward(self, evaluation: Dict, difficulty: float) -> float:
        """
        Reward Function for RL Core.
        Formula: Reward = (Score * Difficulty) - (Penalty for Time/Stress)
        Output Range: [-1.0, 1.0]
        """
        score = evaluation.get("overall_score", 0.5)
        # Higher difficulty + High score = Large positive reward
        # Low score on High difficulty = Small penalty (good attempt)
        # Low score on Low difficulty = Large penalty (fundamental gap)
        
        base_reward = (score - 0.5) * 2.0 # [-1.0, 1.0]
        difficulty_multiplier = 0.5 + (difficulty * 0.5) # [0.5, 1.0]
        
        reward = base_reward * difficulty_multiplier
        
        # Stress penalty (Simulated from telemetry)
        stress_level = evaluation.get("stress_level", 0.1)
        if stress_level > 0.7:
            reward -= 0.1 # Minor penalty for high stress
            
        return round(max(-1.0, min(1.0, reward)), 2)

    def update_difficulty_policy(self, current_difficulty: float, reward: float) -> float:
        """
        Policy Update: Adjust state based on reward signal.
        """
        learning_rate = 0.15
        
        # Gradient ascent on difficulty
        new_difficulty = current_difficulty + (reward * learning_rate)
        
        return round(max(0.1, min(1.0, new_difficulty)), 2)


