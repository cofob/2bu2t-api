"""File containing database setup."""

from os import environ

from sqlalchemy import create_engine

# cockroachdb://root@localhost:26257/defaultdb?sslmode=disable
engine = create_engine(environ["DB_URL"])
