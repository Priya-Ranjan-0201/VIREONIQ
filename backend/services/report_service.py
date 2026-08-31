from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from db.models import ResumeScore, GapAnalysis, InterviewScore, InterviewSession
from typing import Dict, Any
import uuid

async def generate_benchmark_report(db: AsyncSession, user_id: uuid.UUID) -> Dict[str, Any]:
    # 1. Fetch User Data
    from services.analytics_service import get_user_dashboard_stats
    user_stats = await get_user_dashboard_stats(db, user_id)
    
    # 2. Fetch Global Averages (Simulated for now)
    global_avg = {
        "ats_score": 72.5,
        "skill_match": 68.0,
        "technical": 65.0,
        "communication": 70.0,
        "confidence": 62.0
    }
    
    # 3. Calculate Percentile (Simulated logic)
    # In a real app, you would query the entire DB and calculate the actual percentile.
    percentile = 85 if user_stats["ats_score"] > 80 else 60
    
    return {
        "user_metrics": user_stats,
        "global_averages": global_avg,
        "percentile_ranking": percentile,
        "readiness_summary": "You are currently in the top 15% of candidates for your target role. Your technical skills are a major strength, while communication remains an area for incremental growth.",
        "peer_comparison": {
            "ats": user_stats["ats_score"] - global_avg["ats_score"],
            "technical": user_stats["interview_readiness"]["technical"] - global_avg["technical"],
            "communication": user_stats["interview_readiness"]["communication"] - global_avg["communication"]
        }
    }
