"""File containing database setup."""

from os import environ

from sqlalchemy.ext.asyncio import create_async_engine

# cockroachdb+asyncpg://root@localhost:26257/defaultdb?sslmode=disable
engine = create_async_engine(environ["DB_URL"], future=True)
