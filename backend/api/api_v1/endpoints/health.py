from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from db.session import get_db
from core.config import settings
from core.redis import redis_client
from sqlalchemy import text
import time

router = APIRouter()

@router.get("/health", tags=["system"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Deep health check — verifies DB, Redis, and core config.
    Used by Railway/Vercel health probes and smoke tests.
    """
    checks = {}
    overall = "healthy"

    # 1. PostgreSQL
    try:
        await db.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = f"error: {str(e)}"
        overall = "degraded"

    # 2. Redis
    try:
        pong = await redis_client.ping()
        checks["redis"] = "ok" if pong else "no response"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"
        overall = "degraded"

    # 3. Config Sanity (non-sensitive)
    checks["llm_provider"] = settings.DEFAULT_LLM_PROVIDER
    checks["environment"] = settings.ENVIRONMENT
    checks["razorpay_configured"] = bool(settings.RAZORPAY_KEY_ID)
    checks["s3_configured"] = bool(settings.S3_BUCKET_NAME)
    checks["sentry_configured"] = bool(settings.SENTRY_DSN)
    checks["llm_key_present"] = bool(
        settings.ANTHROPIC_API_KEY or settings.OPENAI_API_KEY or settings.GEMINI_API_KEY
    )

    return {
        "status": overall,
        "version": "0.9.0-beta",
        "checks": checks,
        "timestamp": time.time(),
    }

@router.get("/health/live", tags=["system"])
async def liveness():
    """Lightweight liveness probe — used by container orchestrators."""
    return {"status": "ok"}
