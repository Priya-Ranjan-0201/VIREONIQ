import asyncio
from sqlalchemy import text
from db.session import engine

async def optimize_database():
    print("[Maintenance] Starting Database Optimization...")
    
    # List of indexes to ensure high performance
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
        "CREATE INDEX IF NOT EXISTS idx_market_signals_captured ON market_signals(captured_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_interviews_user ON interview_sessions(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id) WHERE is_read = false;"
    ]

    async with engine.begin() as conn:
        for idx in indexes:
            print(f"[Maintenance] Applying: {idx[:50]}...")
            await conn.execute(text(idx))
            
    print("[Maintenance] Database optimized for high-load production traffic.")

if __name__ == "__main__":
    asyncio.run(optimize_database())
