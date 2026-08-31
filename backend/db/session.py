from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB, INET, UUID

from core.config import settings

# Custom compiles rules for SQLite compatibility
@compiles(UUID, 'sqlite')
def compile_uuid_sqlite(type_, compiler, **kw):
    return "VARCHAR(36)"

@compiles(JSONB, 'sqlite')
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

@compiles(INET, 'sqlite')
def compile_inet_sqlite(type_, compiler, **kw):
    return "VARCHAR(45)"

# Conditionally configure engine based on DB type
db_url = settings.async_database_url
is_sqlite = db_url.startswith("sqlite")

if is_sqlite:
    engine = create_async_engine(
        settings.async_database_url,
        echo=False,
        future=True,
    )
else:
    engine = create_async_engine(
        settings.async_database_url,
        echo=False,
        future=True,
        pool_size=20,
        max_overflow=10,
    )

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
