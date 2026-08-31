"""
AI Observability & Cost Tracking.
Logs LLM requests, providers, models, latency percentiles, token usage, cost estimations,
and schema validation results for internal platform auditing.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from db.models import AIObservabilityLog

logger = logging.getLogger(__name__)

# Estimated cost per 1k tokens (blended input/output average in USD)
PROVIDER_COST_PER_1K_TOKENS = {
    "claude": 0.003,
    "gemini": 0.0005,
    "deepseek": 0.0002,
    "nvidia_nim": 0.0007,
    "ollama": 0.0,
    "mock": 0.0
}

def estimate_cost(provider: str, total_tokens: int) -> float:
    rate = PROVIDER_COST_PER_1K_TOKENS.get(provider.lower(), 0.0005)
    return round((total_tokens / 1000.0) * rate, 6)

async def log_ai_execution(
    task_name: str,
    provider: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: float,
    validation_passed: bool = True,
    fallback_triggered: bool = False,
    prompt_version: str = "v1.0",
    db = None
) -> Dict[str, Any]:
    """
    Records an AI observability metric event.
    """
    total_tokens = prompt_tokens + completion_tokens
    cost = estimate_cost(provider, total_tokens)

    log_data = {
        "task_name": task_name,
        "provider": provider,
        "model": model,
        "prompt_version": prompt_version,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "latency_ms": round(latency_ms, 2),
        "cost_estimate_usd": cost,
        "validation_passed": validation_passed,
        "fallback_triggered": fallback_triggered,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    if db:
        try:
            record = AIObservabilityLog(
                task_name=task_name,
                provider=provider,
                model=model,
                prompt_version=prompt_version,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
                cost_estimate_usd=cost,
                validation_passed=validation_passed,
                fallback_triggered=fallback_triggered
            )
            db.add(record)
            await db.commit()
        except Exception as e:
            logger.warning(f"Failed to persist AI observability log to database: {e}")

    return log_data
