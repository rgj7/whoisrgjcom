from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.config import settings
from src.constants import Environment

engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == Environment.DEV,
    pool_pre_ping=True,
    poolclass=NullPool if settings.ENVIRONMENT == Environment.DEV else None,
)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        yield session
