"""Here are the dependencies that are called via FastAPI Depend."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from .database import engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """A generator that returns a database session."""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
