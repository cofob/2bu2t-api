"""Here are the dependencies that are called via FastAPI Depend."""

from os import environ
from typing import AsyncGenerator, Generator

from sqlmodel import Session

from .database import engine
from .ipfs import IPFSClient


def get_session() -> Generator[Session, None, None]:
    """A generator that returns a database session.

    Returns:
        Session: Database session.
    """
    with Session(engine) as session:
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
