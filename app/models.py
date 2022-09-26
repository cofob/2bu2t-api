"""File containing sqlmodel database models."""

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Base user model."""

    name: str


class User(UserBase, table=True):
    """User table."""

    id: int = Field(default=None, primary_key=True)


class UserCreate(UserBase):
    """Model with data required for User row creation."""

    pass
