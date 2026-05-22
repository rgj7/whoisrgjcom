"""Shared test configuration.

Sets required environment variables before any src module is imported,
so that pydantic-settings can initialise without a real .env file.
"""

import os

# Force test DB name so settings.DATABASE_URL derives to the test database.
os.environ["DATABASE_NAME"] = "test_whoisrgj"

# Auth settings (test-safe values)
os.environ.setdefault("AUTH_JWT_SECRET", "test-secret-do-not-use-in-production")
os.environ.setdefault("AUTH_JWT_ALG", "HS256")
os.environ.setdefault("AUTH_JWT_EXP_MINUTES", "60")

# Global settings (override only if not already set via .env)
os.environ.setdefault("ENVIRONMENT", "dev")

from collections.abc import AsyncGenerator

import httpx
import pytest_asyncio
from httpx import ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

# Import models so Base.metadata knows about all tables
from src.auth.models import User  # noqa: F401
from src.main import app
from src.models import Base
from src.posts.models import Post  # noqa: F401


@pytest_asyncio.fixture
async def test_engine():
    """Per-test async engine for all test DB operations."""
    from src.config import settings

    db_url = settings.test_database_url
    engine = create_async_engine(
        db_url,
        pool_pre_ping=True,
        poolclass=NullPool,
    )
    try:
        yield engine
    finally:
        try:
            await engine.dispose()
        except Exception:
            pass  # event loop already closed or other cleanup issues


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient]:
    transport = ASGITransport(app=app)
    ac = httpx.AsyncClient(transport=transport, base_url="http://test")
    try:
        yield ac
    finally:
        try:
            await ac.aclose()
        except RuntimeError:
            pass  # event loop already closed during teardown


@pytest_asyncio.fixture(autouse=True)
async def setup_db(test_engine):
    """Create all tables before each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(autouse=True)
async def clean_db(test_engine):
    """Delete all data before each test."""
    async with test_engine.begin() as conn:
        await conn.execute(text("DELETE FROM post"))
        await conn.execute(text('DELETE FROM "user"'))
