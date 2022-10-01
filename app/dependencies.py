"""Here are the dependencies that are called via FastAPI Depend."""

from os import environ
from typing import AsyncGenerator, Generator

from fastapi import Depends
from sqlmodel import Session

from app.models import User, UserToken

from .database import get_engine_session
from .ipfs import IPFSClient
from .security import oauth2_scheme


def get_session() -> Generator[Session, None, None]:
    """A generator that returns a database session.

    Returns:
        Session: Database session.
    """
    with get_engine_session() as session:
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


async def get_current_user(
    db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)
) -> User:
    """Get current user.

    Returns:
        User: Current user model.
    """
    usertoken = UserToken.from_str_access_token(token)
    return db.query(User).filter(User.uuid == usertoken.user).first()  # type: ignore


async def authorized_only(token: str = Depends(oauth2_scheme)) -> None:
    """Make endpoint viewable only for authorized users."""
    UserToken.from_str_access_token(token)
