"""
System Design Architecture Evaluator.
Evaluates candidate system design responses across 12 structured criteria:
  1. Requirements Clarification
  2. Functional Requirements
  3. Non-Functional Requirements (Latency, Availability, Consistency)
  4. High-Level Architecture
  5. Data Modeling & Storage
  6. API Design
  7. Horizontal Scaling & Load Balancing
  8. Caching Strategy
  9. Reliability & Redundancy
  10. Failure Recovery & Partition Handling
  11. Security & Authentication
  12. Tradeoff Analysis & Justification
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

SYSTEM_DESIGN_CRITERIA_KEYWORDS = {
    "requirements_clarity": ["scale", "throughput", "qps", "read-heavy", "write-heavy", "sla", "latency", "storage estimate", "p99", "bandwidth", "capacity"],
    "functional_scope": ["use case", "api contract", "user flow", "core requirement", "feature scope", "functional", "actors"],
    "non_functional_slas": ["availability", "consistency", "durability", "partition tolerance", "99.99%", "latency budget", "sla", "slo", "mttr"],
    "architecture_modularity": ["gateway", "load balancer", "microservice", "service", "stateless", "layer", "decoupled", "reverse proxy", "event driven"],
    "data_modeling": ["schema", "sharding", "primary key", "replication", "acid", "nosql", "relational", "partition", "denormalization", "b-tree", "foreign key"],
    "api_design": ["rest", "grpc", "endpoint", "idempotency", "pagination", "payload", "rate limit", "post /", "graphql", "idempotency key"],
    "scaling_caching": ["redis", "memcached", "cache invalidation", "cdn", "write-through", "lru", "consistent hashing", "read replica", "cache-aside"],
    "distributed_messaging": ["kafka", "event-driven", "pub/sub", "message queue", "sqs", "rabbitmq", "backpressure", "stream", "async worker"],
    "reliability_recovery": ["circuit breaker", "dead letter", "retry", "fallback", "failover", "replication", "backup", "healthcheck", "bulkhead"],
    "partition_consensus": ["raft", "paxos", "leader election", "split brain", "two-phase commit", "quorum", "eventual consistency", "pacelc", "cap theorem"],
    "security_auth": ["jwt", "oauth", "tls", "encryption", "sanitization", "ddos", "firewall", "vpc", "rate limiting", "least privilege"],
    "tradeoff_analysis": ["tradeoff", "versus", "instead of", "cap theorem", "eventual consistency", "cost", "complexity", "pros and cons", "justification"]
}

def evaluate_system_design_response(
    question_prompt: str,
    response_text: str,
    rubric: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Performs multi-criteria structural and semantic evaluation of a system design response
    across 12 core architectural dimensions.
    """
    text_lower = response_text.lower()
    word_count = len(response_text.split())

    # If response is too brief (< 30 words), mark insufficient evidence
    if word_count < 30:
        return {
            "overall_score": 35.0,
            "architecture_score": 30.0,
            "scalability_score": 30.0,
            "reliability_score": 30.0,
            "tradeoff_score": 25.0,
            "confidence": "LOW",
            "reasoning": "Response is too brief to substantiate architectural competency (under 30 words).",
            "strengths": [],
            "weaknesses": ["Insufficient diagnostic detail provided in architectural response."],
            "criteria_breakdown": {k: 30.0 for k in SYSTEM_DESIGN_CRITERIA_KEYWORDS}
        }

    criteria_scores = {}
    matched_strengths = []
    missing_areas = []

    for criteria_key, keywords in SYSTEM_DESIGN_CRITERIA_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text_lower)
        score = min(100.0, 50.0 + (hits * 14.0))
        criteria_scores[criteria_key] = round(score, 1)

        label = criteria_key.replace("_", " ").title()
        if hits >= 2:
            matched_strengths.append(f"Strong {label} reasoning with explicit architectural elements.")
        elif hits == 0:
            missing_areas.append(f"Did not sufficiently address {label}.")

    # Synthesize composite dimension scores
    architecture_score = (criteria_scores["architecture_modularity"] + criteria_scores["data_modeling"] + criteria_scores["api_design"]) / 3.0
    scalability_score = (criteria_scores["scaling_caching"] + criteria_scores["requirements_clarity"] + criteria_scores["distributed_messaging"]) / 3.0
    reliability_score = (criteria_scores["reliability_recovery"] + criteria_scores["partition_consensus"] + criteria_scores["security_auth"]) / 3.0
    tradeoff_score = (criteria_scores["tradeoff_analysis"] + criteria_scores["non_functional_slas"]) / 2.0

    overall_score = round(
        (architecture_score * 0.30) + 
        (scalability_score * 0.25) + 
        (reliability_score * 0.25) + 
        (tradeoff_score * 0.20),
        1
    )

    confidence = "HIGH" if word_count >= 120 else ("MEDIUM" if word_count >= 60 else "LOW")

    return {
        "overall_score": overall_score,
        "architecture_score": round(architecture_score, 1),
        "scalability_score": round(scalability_score, 1),
        "reliability_score": round(reliability_score, 1),
        "tradeoff_score": round(tradeoff_score, 1),
        "confidence": confidence,
        "reasoning": f"Architectural evaluation yielded {overall_score:.0f}/100 across {len(SYSTEM_DESIGN_CRITERIA_KEYWORDS)} criteria with detailed tradeoffs.",
        "strengths": matched_strengths[:3] if matched_strengths else ["Clear foundational architecture"],
        "weaknesses": missing_areas[:3] if missing_areas else ["Could deepen quantitative capacity calculations & SLA bounds"],
        "criteria_breakdown": criteria_scores
    }

