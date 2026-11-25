import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from db.session import engine
from db.models import Base
import db.models  # Ensure all models are loaded

async def init_db():
    if settings.is_production or os.getenv("ALLOW_DESTRUCTIVE_DB_INIT", "").lower() != "true":
        raise RuntimeError(
            "init_db_schema.py drops all tables and requires non-production ENVIRONMENT "
            "plus ALLOW_DESTRUCTIVE_DB_INIT=true."
        )
    print("Initializing database schema...")
    async with engine.begin() as conn:
        # For development, we drop and recreate to ensure schema alignment
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database schema initialized successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())
