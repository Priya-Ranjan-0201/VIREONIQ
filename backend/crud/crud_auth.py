import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from db.models import RefreshToken, Session, AuditLog

async def create_refresh_token(db: AsyncSession, user_id: uuid.UUID, token: str, expires_at: datetime) -> RefreshToken:
    db_obj = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_obj)
    await db.flush()
    return db_obj

async def revoke_refresh_token(db: AsyncSession, token: str) -> None:
    stmt = update(RefreshToken).where(RefreshToken.token == token).values(revoked_at=datetime.now(timezone.utc))
    await db.execute(stmt)

async def create_session(db: AsyncSession, user_id: uuid.UUID, device_id: str = None, ip_address: str = None, user_agent: str = None) -> Session:
    db_obj = Session(
        user_id=user_id,
        device_id=device_id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(db_obj)
    await db.flush()
    return db_obj

async def log_audit_event(db: AsyncSession, user_id: uuid.UUID, action: str, ip_address: str = None, user_agent: str = None) -> AuditLog:
    db_obj = AuditLog(
        user_id=user_id,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(db_obj)
    await db.flush()
    return db_obj
