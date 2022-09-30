"""Module with jwt token related database models."""

from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from os import environ
from time import time
from uuid import UUID, uuid4

from jose import JWTError, jwt
from loguru import logger
from sqlmodel import Field, Session, SQLModel

from app.exceptions import JWTException, JWTValidationError

from ..database import get_engine_session

ALGORITHM = "HS256"
SECRET_KEY = environ["SECRET"]
REFRESH_TOKEN_EXPIRE_DAYS = 90
ACCESS_TOKEN_EXPIRE_MINUTES = 15

ParsedJWTType = dict[str, str | int | float]


def generate_refresh_token_expire_ts() -> int:
    """Get JWT refresh token expire timestamp."""
    return int((datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).timestamp())


def generate_access_token_expire_ts() -> int:
    """Get JWT access token expire timestamp."""
    return int((datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp())


class TokenTypes(Enum):
    """Token types."""

    RefreshToken = 0
    AccessToken = 1


class TokenABC(SQLModel, metaclass=ABCMeta):
    """Abstract token model.

    It is intended for refresh JWT tokens. If the UUID is in this table,
    then the JWT is valid and can be accepted.
    """

    @abstractmethod
    def issue_refresh_token(self, data: ParsedJWTType = {}) -> str:
        """Issue JWT refresh token.

        Refresh token used for access token issue.

        Examples:
            >>> token = Token()
            >>> token.issue_refresh_token({"some_key": "some_data"})
            >>> "eyJhbGcCJ9.eyJ1aWQiOiI3MzyIn0.w-IX1M5Tmals6HBA"

        Args:
            dict: JWT data.

        Returns:
            str: JWT token string.
        """

    @abstractmethod
    def issue_access_token(self, data: ParsedJWTType = {}) -> str:
        """Issue JWT access token.

        Access token used for authorization.

        Examples:
            >>> token = Token()
            >>> token.issue_access_token({"some_key": "some_data"})
            >>> "eyJhbGcCJ9.eyJ1aWQiOiI3MzyIn0.w-IX1M5Tmals6HBA"

        Args:
            dict: JWT data.

        Returns:
            str: JWT token string.
        """

    @classmethod
    @abstractmethod
    def cleanup(cls) -> None:
        """Remove expired tokens from database."""

    @staticmethod
    @abstractmethod
    def parse(token: str) -> ParsedJWTType:
        """Parse JWT string to dict.

        Examples:
            >>> Token.parse("eyJhbGcCJ9.eyJ1aWQiOiI3MzyIn0.w-IX1M5Tmals6HBA")
            >>> {
            >>>   "sub": "1234567890",
            >>>   "name": "John Doe",
            >>>   "iat": 1516239022
            >>> }

        Args:
            token: JWT token string.

        Raises:
            JWTValidationError: If token is invalid.
        """

    @classmethod
    @abstractmethod
    def verify(cls, parsed: ParsedJWTType, typ: TokenTypes, db: Session | None = None) -> None:
        """Verify that token is valid.

        Examples:
            >>> parsed = Token.parse("eyJhbGcCJ9.eyJ1aWQiOiI3MzyIn0.w-IX1M5Tmals6HBA")
            >>> Token.verify(parsed, TokenType.AccessToken)

        Args:
            parsed: Parsed JWT token.
            db: Database session.
            typ: Token type.

        Raises:
            JWTValidationError: If token is invalid.
        """


class TokenBase(TokenABC):
    """Realisation of common methods from TokenABC."""

    uuid: UUID = Field(
        default_factory=uuid4, primary_key=True, index=True, nullable=False, unique=True
    )
    expire_in: int = Field(default_factory=generate_refresh_token_expire_ts, nullable=False)

    def issue_refresh_token(self, data: ParsedJWTType = {}) -> str:
        to_encode = data.copy()
        to_encode.update(
            {
                "exp": self.expire_in,
                "iat": int(time()),
                "typ": TokenTypes.RefreshToken.value,
                "class": self.__class__.__name__,
            }
        )
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore

    def issue_access_token(self, data: ParsedJWTType = {}) -> str:
        to_encode = data.copy()
        to_encode.update(
            {
                "exp": generate_access_token_expire_ts(),
                "iat": int(time()),
                "typ": TokenTypes.AccessToken.value,
                "class": self.__class__.__name__,
            }
        )
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore

    @classmethod
    def cleanup(cls) -> None:
        with get_engine_session() as db:
            db.query(cls).filter(cls.expire_in <= int(time())).delete()

    @staticmethod
    def parse(token: str) -> ParsedJWTType:
        try:
            return jwt.decode(  # type: ignore
                token,
                SECRET_KEY,
                algorithms=ALGORITHM,
                options={"require_iat": True, "require_exp": True, "require_sub": True},
            )
        except JWTError:
            logger.exception("JWT exception")
            raise JWTValidationError(detail="JWT decode/verification error")

    @classmethod
    def verify(cls, parsed: ParsedJWTType, typ: TokenTypes, db: Session | None = None) -> None:
        typ_value = parsed.get("typ")
        if typ_value is None:
            raise JWTValidationError(detail="typ field is not provided")
        if typ_value != typ.value:
            raise JWTValidationError(detail=f"{typ.name} token is required")


class UserToken(TokenBase, table=True):
    """User JWT token table."""

    user: UUID = Field(nullable=False, foreign_key="user.uuid")

    def issue_refresh_token(self, data: ParsedJWTType = {}) -> str:
        assert self.user is not None
        data.update({"sub": str(self.user)})
        return super().issue_refresh_token(data)

    def issue_access_token(self, data: ParsedJWTType = {}) -> str:
        assert self.user is not None
        data.update({"sub": str(self.user)})
        return super().issue_access_token(data)

    @classmethod
    def verify(cls, parsed: ParsedJWTType, typ: TokenTypes, db: Session | None = None) -> None:
        super().verify(parsed, typ, db)
        if typ == TokenTypes.RefreshToken:
            assert db
            if db.query(cls).filter(cls.user == parsed["sub"]).first() is None:
                raise JWTException("JWT revoked")
