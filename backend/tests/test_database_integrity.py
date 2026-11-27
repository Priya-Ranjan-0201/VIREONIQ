import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.dialects.sqlite import dialect as sqlite_dialect
from sqlalchemy.dialects.postgresql import JSONB, INET, UUID
from sqlalchemy.schema import CreateTable
from sqlalchemy import Table, Column, MetaData

from core.config import settings
from db.session import get_db, Base
import db.models  # noqa: F401 ensuring all models are imported into Base.metadata


def test_sqlite_type_compilation():
    """Verify that PostgreSQL UUID, JSONB, and INET compile safely to SQLite equivalents."""
    metadata = MetaData()
    test_table = Table(
        "test_compilation",
        metadata,
        Column("uuid_col", UUID),
        Column("jsonb_col", JSONB),
        Column("inet_col", INET),
    )
    sql = str(CreateTable(test_table).compile(dialect=sqlite_dialect()))
    assert "VARCHAR(36)" in sql
    assert "JSON" in sql
    assert "VARCHAR(45)" in sql


def test_database_pool_settings():
    """Verify production database pool default configuration values."""
    assert settings.DB_POOL_SIZE >= 10
    assert settings.DB_MAX_OVERFLOW >= 5
    assert settings.DB_POOL_TIMEOUT >= 10
    assert settings.DB_POOL_RECYCLE <= 600
    assert settings.DB_POOL_PRE_PING is True


@pytest.mark.asyncio
async def test_get_db_commits_on_success():
    """Verify that get_db commits the session when no exception is raised."""
    mock_session = AsyncMock()
    mock_maker = MagicMock()
    mock_maker.return_value.__aenter__.return_value = mock_session
    mock_maker.return_value.__aexit__.return_value = None

    with patch("db.session.async_session_maker", mock_maker):
        async for session in get_db():
            assert session is mock_session

        mock_session.commit.assert_awaited_once()
        mock_session.rollback.assert_not_awaited()
        mock_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_db_rolls_back_on_exception():
    """Verify that get_db rolls back the session when an unhandled exception occurs."""
    mock_session = AsyncMock()
    mock_maker = MagicMock()
    mock_maker.return_value.__aenter__.return_value = mock_session
    mock_maker.return_value.__aexit__.return_value = None

    with patch("db.session.async_session_maker", mock_maker):
        gen = get_db()
        session = await gen.__anext__()
        assert session is mock_session

        with pytest.raises(RuntimeError, match="Simulated DB failure"):
            await gen.athrow(RuntimeError("Simulated DB failure"))

        mock_session.commit.assert_not_awaited()
        mock_session.rollback.assert_awaited_once()
        mock_session.close.assert_awaited_once()


def test_core_model_tables_and_relations():
    """Verify that core tables exist in SQLAlchemy metadata and have expected primary keys."""
    table_names = Base.metadata.tables.keys()
    required_tables = ["users", "interview_sessions", "resumes", "audit_logs", "job_listings"]
    for t in required_tables:
        assert t in table_names, f"Expected table '{t}' in Base.metadata"

    users_table = Base.metadata.tables["users"]
    assert "id" in users_table.c
    assert "email" in users_table.c
    assert users_table.c.id.primary_key
