"""Module containing exceptions inherited from AbstractException."""

from abc import ABCMeta

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from .app import app


class ErrorModel(BaseModel):
    """Error response for AbstractException."""

    ok: bool = False
    status_code: int = 500
    error_code: str = "Exception"
    error_code_description: str | None = None
    detail: str | None = None


class AbstractException(Exception, metaclass=ABCMeta):
    """Abstract exception.

    All custom exception must inherit from this class.
    """

    def __init__(
        self,
        detail: str | None = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Init method."""
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code
        self.headers = headers

        logger.error(self.detail)


class IPFSException(AbstractException):
    """Exception related to IPFS."""


class InvalidCIDException(IPFSException):
    """Invalid CID."""

    def __init__(self) -> None:
        """Init method."""
        super().__init__(detail="Invalid CID")


class JWTException(AbstractException):
    """Exception related to JWT."""


class JWTValidationError(AbstractException):
    """JWT validation error."""


@app.exception_handler(AbstractException)
async def abstract_exception_handler(request: Request, exc: AbstractException) -> JSONResponse:
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
            error_code_description=exc.__class__.__doc__,
        ).dict(),
        headers=exc.headers,
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Exception handler for StarletteHTTPException.

    Returns:
        JSON serialized ErrorModel.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorModel(
            error_code="Exception",
            detail=exc.detail,
            status_code=exc.status_code,
        ).dict(),
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Exception handler for RequestValidationError.

    Returns:
        JSON serialized ErrorModel.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorModel(
            error_code="RequestValidationException",
            detail="Invalid request",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        ).dict(),
    )
