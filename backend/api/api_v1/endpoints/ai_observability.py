from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any

from api.deps import get_db, get_current_active_user
from db.models import User, AIObservabilityLog

router = APIRouter()

@router.get("/metrics")
async def get_ai_observability_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Returns AI Gateway operational metrics: request volume, success rate, P95 latency,
    fallback percentage, estimated cost, and provider distribution.
    """
    stmt = select(AIObservabilityLog).order_by(AIObservabilityLog.created_at.desc()).limit(100)
    records = list((await db.execute(stmt)).scalars().all())

    total_requests = len(records)
    if total_requests == 0:
        return {
            "total_requests": 0,
            "success_rate_percent": 0.0,
            "p95_latency_sec": 0.0,
            "fallback_rate_percent": 0.0,
            "total_tokens_consumed": 0,
            "estimated_cost_usd": 0.0,
            "active_providers": [],
            "recent_logs": [],
            "data_status": "empty",
        }

    valid_count = sum(1 for r in records if r.validation_passed)
    fallback_count = sum(1 for r in records if r.fallback_triggered)
    total_cost = sum(float(r.cost_estimate_usd or 0.0) for r in records)
    total_tokens = sum((r.prompt_tokens or 0) + (r.completion_tokens or 0) for r in records)
    latencies = sorted([r.latency_ms for r in records if r.latency_ms])
    p95_idx = int(len(latencies) * 0.95) if latencies else 0
    p95_latency = latencies[p95_idx] / 1000.0 if latencies else 1.5

    return {
        "total_requests": total_requests,
        "success_rate_percent": round((valid_count / total_requests) * 100.0, 1),
        "p95_latency_sec": round(p95_latency, 2),
        "fallback_rate_percent": round((fallback_count / total_requests) * 100.0, 1),
        "total_tokens_consumed": total_tokens,
        "estimated_cost_usd": round(total_cost, 4),
        "recent_logs": [
            {
                "id": str(r.id),
                "task_name": r.task_name,
                "provider": r.provider,
                "model": r.model,
                "latency_ms": r.latency_ms,
                "validation_passed": r.validation_passed,
                "cost_estimate_usd": float(r.cost_estimate_usd or 0.0),
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in records[:10]
        ]
    }
