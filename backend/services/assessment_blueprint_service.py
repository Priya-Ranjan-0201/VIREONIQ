"""
Assessment Blueprint Service (v4.0.0).
Defines standardized role blueprints, competency distributions, difficulty ranges,
and rubric-backed assessment challenges with hidden test suites.
"""

from typing import Dict, Any, List, Optional
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models import AssessmentBlueprint, AssessmentQuestion
from services.canonical_skill_service import normalize_skill_name

logger = logging.getLogger(__name__)

BLUEPRINT_VERSION = "4.0.0"

# Standard Role Blueprints
ROLE_BLUEPRINTS: Dict[str, Dict[str, Any]] = {
    "Backend Engineer": {
        "competency_weights": {
            "Python": 0.20,
            "System Design": 0.25,
            "Data Structures": 0.20,
            "PostgreSQL": 0.15,
            "REST APIs": 0.10,
            "Communication": 0.10
        },
        "difficulty_range": ["BEGINNER", "INTERMEDIATE", "ADVANCED"],
        "time_limit_minutes": 45,
        "min_questions": 5
    },
    "Full Stack Engineer": {
        "competency_weights": {
            "TypeScript": 0.20,
            "React": 0.20,
            "Python": 0.20,
            "System Design": 0.20,
            "REST APIs": 0.10,
            "Communication": 0.10
        },
        "difficulty_range": ["BEGINNER", "INTERMEDIATE", "ADVANCED"],
        "time_limit_minutes": 45,
        "min_questions": 5
    },
    "AI/ML Engineer": {
        "competency_weights": {
            "Python": 0.25,
            "Machine Learning": 0.25,
            "Data Structures": 0.20,
            "System Design": 0.15,
            "Communication": 0.15
        },
        "difficulty_range": ["INTERMEDIATE", "ADVANCED", "EXPERT"],
        "time_limit_minutes": 50,
        "min_questions": 5
    }
}

# Standard Pre-Configured Question Bank with Pre-Defined Rubrics & Hidden Tests
CURATED_QUESTION_BANK: List[Dict[str, Any]] = [
    {
        "role_name": "Backend Engineer",
        "competency": "Python",
        "difficulty": "INTERMEDIATE",
        "question_type": "CODING_CHALLENGE",
        "prompt": "Implement a function `two_sum_indexed(nums: List[int], target: int) -> List[int]` that finds indices of two numbers that add up to target in O(N) time complexity.",
        "starter_code": "def two_sum_indexed(nums: list[int], target: int) -> list[int]:\n    # Implement O(N) solution using hashmap\n    pass\n",
        "rubric": {
            "time_complexity_expected": "O(N)",
            "space_complexity_expected": "O(N)",
            "hashmap_usage": True,
            "handles_duplicates": True
        },
        "hidden_tests": [
            {"input": "[2, 7, 11, 15], 9", "expected": "[0, 1]"},
            {"input": "[3, 2, 4], 6", "expected": "[1, 2]"},
            {"input": "[3, 3], 6", "expected": "[0, 1]"},
            {"input": "[-1, -2, -3, -4, -5], -8", "expected": "[2, 4]"}
        ]
    },
    {
        "role_name": "Backend Engineer",
        "competency": "System Design",
        "difficulty": "ADVANCED",
        "question_type": "SYSTEM_DESIGN",
        "prompt": "Design a Distributed Rate Limiter service supporting 100,000 requests per second across multi-region API gateways. Explain your choice of algorithm, caching layer, and failure handling under network partitions.",
        "starter_code": None,
        "rubric": {
            "algorithm_choice": "Token Bucket or Sliding Window Log",
            "storage_layer": "Redis Cluster with Lua Scripts",
            "concurrency_handling": "Atomic Redis operations or Local Token Bucket with sync",
            "fault_tolerance": "Fail-open vs fail-closed tradeoff analysis",
            "latency_budget": "< 5ms p99 overhead"
        },
        "hidden_tests": []
    },
    {
        "role_name": "Backend Engineer",
        "competency": "Data Structures",
        "difficulty": "INTERMEDIATE",
        "question_type": "CODING_CHALLENGE",
        "prompt": "Implement `is_valid_parentheses(s: str) -> bool` using a Stack to determine if bracket string s is valid with O(N) time and O(N) space.",
        "starter_code": "def is_valid_parentheses(s: str) -> bool:\n    pass\n",
        "rubric": {
            "time_complexity_expected": "O(N)",
            "space_complexity_expected": "O(N)",
            "stack_usage": True
        },
        "hidden_tests": [
            {"input": "'()[]{}'", "expected": "True"},
            {"input": "'(]'", "expected": "False"},
            {"input": "'([{}])'", "expected": "True"},
            {"input": "']'", "expected": "False"}
        ]
    },
    {
        "role_name": "Backend Engineer",
        "competency": "PostgreSQL",
        "difficulty": "INTERMEDIATE",
        "question_type": "CONCEPTUAL",
        "prompt": "Explain the difference between a B-Tree index and a Hash index in PostgreSQL. When would a B-Tree index fail to be utilized during a `WHERE column LIKE '%term'` query?",
        "starter_code": None,
        "rubric": {
            "btree_properties": "Ordered, supports range queries (<, >, BETWEEN) and equality",
            "hash_properties": "Equality only (=)",
            "wildcard_explanation": "Leading wildcards (%term) prevent index tree traversal; requires pg_trgm GIN index"
        },
        "hidden_tests": []
    },
    {
        "role_name": "Backend Engineer",
        "competency": "Communication",
        "difficulty": "INTERMEDIATE",
        "question_type": "BEHAVIORAL",
        "prompt": "Describe a challenging engineering failure or production outage you handled. Detail your specific triage actions, root cause analysis, and preventative safeguards implemented.",
        "starter_code": None,
        "rubric": {
            "star_framework": "Clear Situation, Task, Action, Result",
            "ownership": "Personal accountability and leadership",
            "systemic_thinking": "Blameless post-mortem and automated regression prevention"
        },
        "hidden_tests": []
    }
]

def get_role_blueprint(role_name: str) -> Dict[str, Any]:
    """
    Returns the standard blueprint specification for a target role.
    """
    norm_role = role_name if role_name in ROLE_BLUEPRINTS else "Backend Engineer"
    bp = ROLE_BLUEPRINTS[norm_role]
    return {
        "role_name": norm_role,
        "version": BLUEPRINT_VERSION,
        "competency_weights": bp["competency_weights"],
        "difficulty_range": bp["difficulty_range"],
        "time_limit_minutes": bp["time_limit_minutes"],
        "min_questions": bp["min_questions"]
    }

def get_blueprint_questions(role_name: str, target_competency: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns candidate questions matching the role blueprint.
    """
    results = []
    for q in CURATED_QUESTION_BANK:
        if q["role_name"] == role_name or role_name not in ROLE_BLUEPRINTS:
            if not target_competency or normalize_skill_name(q["competency"]) == normalize_skill_name(target_competency):
                results.append(q)
    return results or CURATED_QUESTION_BANK
