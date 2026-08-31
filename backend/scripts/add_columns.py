import asyncio
import sys
import os

# Add backend dir to path to import db
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from db.session import engine
from sqlalchemy import text

async def run_sql():
    async with engine.begin() as conn:
        await conn.execute(text("ALTER TABLE psychometric_profiles ADD COLUMN IF NOT EXISTS placement_probability_history JSONB DEFAULT '[]'::jsonb;"))
        print('Successfully added placement_probability_history column!')

if __name__ == "__main__":
    asyncio.run(run_sql())
