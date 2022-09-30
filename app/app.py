"""Module containing FastAPI app instance.

A separate file is needed to avoid creating circular imports.
"""

from fastapi import FastAPI

app = FastAPI()

__all__ = ["app"]

from . import main  # noqa
