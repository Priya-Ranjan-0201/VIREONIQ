import pytest
import asyncio
import uuid
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

import db.session
from db.models import Base, User, Role, Profile
from sqlalchemy.pool import StaticPool

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        TEST_DB_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    from sqlalchemy import select
    # Check or create default role
    role_stmt = select(Role).where(Role.name == "candidate")
    role = (await db_session.execute(role_stmt)).scalars().first()
    if not role:
        role = Role(id=uuid.uuid4(), name="candidate", description="Test candidate")
        db_session.add(role)
        await db_session.flush()

    user = User(
        id=uuid.uuid4(),
        email=f"candidate_{uuid.uuid4().hex[:6]}@vireoniq.com",
        password_hash="argon2id_mock_hash",
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    
    profile = Profile(
        user_id=user.id,
        first_name="Alex",
        last_name="Chen",
        target_role="Backend Engineer",
        placement_readiness_score=78.50
    )
    db_session.add(profile)
    await db_session.commit()
    return user
