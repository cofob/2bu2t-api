"""Module with user-related database models."""

from time import time
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


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
    disabled: bool = Field(default=False, nullable=False)
    created_at: int = Field(default_factory=time, nullable=False)


class User(UserBase, table=True):
    """User table."""

    uuid: UUID = Field(
        default_factory=uuid4, primary_key=True, index=True, nullable=False, unique=True
    )


class UserCreate(UserBase):
    """Model with data required for User row creation."""
