"""Module containing FastAPI app instance.

A separate file is needed to avoid creating circular imports.
"""

from fastapi import FastAPI
from slowapi import Limiter
from slowapi.util import get_remote_address

app = FastAPI()
limiter = Limiter(key_func=get_remote_address)

__all__ = ["app"]

from . import main  # noqa
