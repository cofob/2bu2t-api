"""Module with user-related database models."""

from uuid import UUID, uuid4

from loguru import logger
from sqlmodel import Field, SQLModel

from app.database import get_engine_session
from app.utils import int_time


class UserBase(SQLModel):
    """Base user model."""

    email: str = Field(
        index=True,
        nullable=False,
        unique=True,
        max_length=64,
        regex=r"^[\w\-\.\+]+@([\w-]+\.)+[\w-]{2,4}$",
    )
    nickname: str = Field(
        index=True,
        nullable=False,
        unique=True,
        min_length=3,
        max_length=16,
        regex=r"^[a-zA-Z0-9_]+$",
    )
    password: str = Field(max_length=128, nullable=False)


class User(UserBase, table=True):
    """User table."""

    uuid: UUID = Field(
        default_factory=uuid4, primary_key=True, index=True, nullable=False, unique=True
    )
    disabled: bool = Field(default=False, nullable=False)
    verifed: bool = Field(default=False, nullable=False)
    created_at: int = Field(default_factory=int_time, nullable=False)

    @classmethod
    def cleanup(cls) -> None:
        with get_engine_session() as db:
            q = db.query(cls).filter(cls.created_at + 3600 <= int_time(), cls.verifed == False)
            count = q.count()
            q.delete()
            logger.info(f"Deleted {count} unverifed User accounts.")


class UserCreate(UserBase):
    """Model with data required for User row creation."""
