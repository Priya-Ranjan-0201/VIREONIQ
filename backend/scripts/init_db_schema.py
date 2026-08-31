import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.session import engine
from db.models import Base
import db.models  # Ensure all models are loaded

async def init_db():
    print("Initializing database schema...")
    async with engine.begin() as conn:
        # For development, we drop and recreate to ensure schema alignment
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Database schema initialized successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())
