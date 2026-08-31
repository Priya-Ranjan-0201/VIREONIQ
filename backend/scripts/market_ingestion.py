import asyncio
import json
import uuid
from datetime import datetime
from sqlalchemy import text
from db.session import engine

class MarketIngestionPipeline:
    """
    Self-Updating Intelligence Pipeline.
    Ingests market signals and updates the platform's understanding of 'Hiring Readiness'.
    """
    
    async def ingest_signals(self):
        print("[Intelligence] Starting Market Ingestion Cycle...")
        
        # Simulate data from GitHub, LinkedIn, and JDs
        mock_signals = [
            {
                "skill": "FastAPI",
                "source": "GitHub Trends",
                "velocity": 1.25, # Trending Up
                "relevance": 0.95
            },
            {
                "skill": "System Design",
                "source": "FAANG Job Descriptions",
                "velocity": 1.10,
                "relevance": 0.98
            },
            {
                "skill": "PostgreSQL Optimization",
                "source": "Startup Hiring Patterns",
                "velocity": 1.40,
                "relevance": 0.90
            }
        ]

        async with engine.begin() as conn:
            for signal in mock_signals:
                print(f"[Intelligence] Learning new signal: {signal['skill']} from {signal['source']}")
                
                await conn.execute(
                    text("""
                    INSERT INTO market_signals (id, skill_name, source, demand_velocity, relevance_score, last_updated)
                    VALUES (:id, :skill, :source, :velocity, :relevance, :now)
                    ON CONFLICT (skill_name) DO UPDATE SET
                        demand_velocity = EXCLUDED.demand_velocity,
                        relevance_score = EXCLUDED.relevance_score,
                        last_updated = EXCLUDED.last_updated
                    """),
                    {
                        "id": uuid.uuid4(),
                        "skill": signal["skill"],
                        "source": signal["source"],
                        "velocity": signal["velocity"],
                        "relevance": signal["relevance"],
                        "now": datetime.utcnow()
                    }
                )

        print("[Intelligence] Market Ingestion Cycle Complete.")

if __name__ == "__main__":
    pipeline = MarketIngestionPipeline()
    asyncio.run(pipeline.ingest_signals())
