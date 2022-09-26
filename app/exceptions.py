"""File containing exceptions inherited from AbstractException."""

from abc import ABCMeta

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .app import app


class ErrorModel(BaseModel):
    """Error response for AbstractException."""

    ok: bool = False
    status_code: int = 500
    error_code: str = "Exception"
    detail: str | None = None


class AbstractException(Exception, metaclass=ABCMeta):
    """Abstract exception.

    All custom exception must inherit from this class.
    """

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str | None = None,
    ) -> None:
        """Init method."""
        self.detail = detail
        self.status_code = status_code


@app.exception_handler(AbstractException)
async def global_exception_handler(request: Request, exc: AbstractException) -> JSONResponse:
    """Exception handler for AbstractException.

    Returns:
        JSON serialized ErrorModel.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorModel(
            error_code=exc.__class__.__name__,
            detail=exc.detail,
            status_code=exc.status_code,
        ).dict(),
    )
