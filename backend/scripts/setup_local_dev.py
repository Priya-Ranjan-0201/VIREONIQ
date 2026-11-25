import os
import sys
import asyncio

os.environ["ALLOW_DESTRUCTIVE_DB_INIT"] = "true"
os.environ["ENVIRONMENT"] = "development"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./vireoniq_dev.db"

# Ensure backend root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.init_db_schema import init_db
from scripts.seed_user import seed_user
from scripts.seed_jobs import seed_jobs
from scripts.seed_demo_data import seed_demo_data

async def main():
    print("--- 1. Initializing DB schema ---")
    await init_db()
    print("--- 2. Seeding users ---")
    await seed_user()
    print("--- 3. Seeding jobs & market signals ---")
    await seed_jobs()
    print("--- 4. Seeding demo data for test user ---")
    await seed_demo_data()
    print("--- ALL LOCAL SEEDING COMPLETED SUCCESSFULLY ---")

if __name__ == "__main__":
    asyncio.run(main())
