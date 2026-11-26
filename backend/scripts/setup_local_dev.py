import asyncio
import os
import sys

import structlog

logger = structlog.get_logger(__name__)


async def main() -> None:
    if os.environ.get("ENVIRONMENT", "").lower() == "production":
        raise RuntimeError("setup_local_dev.py must never be run in production.")

    os.environ["ALLOW_DESTRUCTIVE_DB_INIT"] = "true"
    os.environ["ENVIRONMENT"] = "development"
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./vireoniq_dev.db"

    # Ensure backend root is on sys.path before importing scripts
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    from scripts.init_db_schema import init_db
    from scripts.seed_demo_data import seed_demo_data
    from scripts.seed_jobs import seed_jobs
    from scripts.seed_user import seed_user

    logger.info("setup_local_dev_step", step="init_db_schema")
    await init_db()
    logger.info("setup_local_dev_step", step="seed_user")
    await seed_user()
    logger.info("setup_local_dev_step", step="seed_jobs")
    await seed_jobs()
    logger.info("setup_local_dev_step", step="seed_demo_data")
    await seed_demo_data()
    logger.info("setup_local_dev_completed")


if __name__ == "__main__":
    asyncio.run(main())
