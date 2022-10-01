"""Module with user-related database models."""

from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Base user model."""

    email: str = Field(primary_key=True, index=True, nullable=False, unique=True)
    nickname: str = Field(primary_key=True, index=True, nullable=False, unique=True)
    disabled: bool = Field(default=False, nullable=False)


class User(UserBase, table=True):
    """User table."""

    uuid: UUID = Field(
        default_factory=uuid4, primary_key=True, index=True, nullable=False, unique=True
    )


class UserCreate(UserBase):
    """Model with data required for User row creation."""
