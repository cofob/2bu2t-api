"""Module containing exceptions inherited from AbstractException."""

from abc import ABCMeta

from fastapi import Request, status
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
        """Exception init method.

        Args:
            detail: Short error description.
            status_code: HTTP status code that will be returned.
            headers: Dict with HTTP headers that will be returned.
        """
        if detail is not None:
            super().__init__(detail)
        self.detail = detail
        self.status_code = status_code
        self.headers = headers

        logger.error(self.detail)


class IPFSException(AbstractException):
    """Exception related to IPFS."""


class InvalidCIDException(IPFSException):
    """Invalid CID."""


class JWTException(AbstractException):
    """Exception related to JWT."""


class JWTValidationError(JWTException):
    """JWT validation error.

    This can happen in several cases:
    - If JWT cannot be parsed
    - If the `exp` field is expired or not present
    - If the `iat` field is invalid or not present
    - If the `sub` field is invalid or not present
    - If the `typ` field is invalid or not present
    - If the `jti` or `sid` field is invalid or not present
    - If the `class` field is not present
    """


class JWTRevokedException(JWTValidationError):
    """JWT is revoked and cannot be accepted.

    This can happen in several cases:
    - If the `sub` field is not found in the database
      (i.e. the one for whom this token was issued is not found)
    - If the `jti` field is not found in the database
      (the token was cancelled prematurely if the `exp` field has not come out yet)
    """


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
            detail=exc.detail if exc.detail is not None else exc.__class__.__doc__,
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
