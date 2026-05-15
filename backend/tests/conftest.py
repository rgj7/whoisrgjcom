"""Shared test configuration.

Sets required environment variables before any src module is imported,
so that pydantic-settings can initialise without a real .env file.
"""

import os

# Auth settings (test-safe values)
os.environ.setdefault("AUTH_JWT_SECRET", "test-secret-do-not-use-in-production")
os.environ.setdefault("AUTH_JWT_ALG", "HS256")
os.environ.setdefault("AUTH_JWT_EXP_MINUTES", "60")

# Global settings (override only if not already set via .env)
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("ENVIRONMENT", "dev")

# Import after env vars are set
import asyncio

import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import create_async_engine

# Import models so Base.metadata knows about all tables
from src.auth.models import User  # noqa: F401
from src.models import Base
from src.posts.models import Post  # noqa: F401


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    """Create all tables before the test session starts."""
    from src.config import settings

    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    """Delete all data before each test."""
    from sqlalchemy import text

    from src.database import async_session

    async with async_session() as session:
        await session.execute(text("DELETE FROM post"))
        await session.execute(text("DELETE FROM user"))
        await session.commit()
