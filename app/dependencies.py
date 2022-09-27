"""Here are the dependencies that are called via FastAPI Depend."""

from os import environ
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from .database import engine
from .ipfs import IPFSClient


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """A generator that returns a database session.

    Returns:
        AsyncSession: Database session.
    """
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


IPFS_AUTH = None
if environ.get("IPFS_USERNAME") is not None:
    IPFS_AUTH = (environ["IPFS_USERNAME"], environ["IPFS_PASSWORD"])


async def get_ipfs() -> AsyncGenerator[IPFSClient, None]:
    """A generator that returns IPFS session.

    Returns:
        IPFSClient: Prepared IPFS session.
    """
    async with IPFSClient(environ["IPFS_URL"], IPFS_AUTH) as client:
        yield client
