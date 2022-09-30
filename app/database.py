"""Module containing database setup."""

from os import environ

from sqlalchemy import create_engine
from sqlmodel import Session

# cockroachdb://root@localhost:26257/defaultdb?sslmode=disable
engine = create_engine(environ["DB_URL"])


def get_engine_session() -> Session:
    """Get sqlmodel.Session instance with current engine."""
    return Session(engine)
