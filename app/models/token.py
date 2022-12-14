"""Module with jwt token related database models."""

from abc import ABCMeta, abstractmethod
from calendar import timegm
from datetime import datetime, timedelta
from enum import Enum
from os import environ
from typing import Type, TypeVar
from uuid import UUID, uuid4

from jose import JWTError, jwt
from loguru import logger
from sqlmodel import Field, Session, SQLModel

from app.exceptions import JWTRevokedException, JWTValidationError
from app.models.user import User

from ..database import get_engine_session

ALGORITHM = "HS256"
SECRET_KEY = environ["SECRET"]
REFRESH_TOKEN_EXPIRE_DAYS = 90
ACCESS_TOKEN_EXPIRE_MINUTES = 15

ParsedJWTType = dict[str, str | int | float]
T = TypeVar("T", bound="TokenABC")


def generate_refresh_token_expire_ts() -> int:
    """Get JWT refresh token expire timestamp."""
    return timegm((datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).utctimetuple())


def generate_access_token_expire_ts() -> int:
    """Get JWT access token expire timestamp."""
    return timegm(
        (datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).utctimetuple()
    )


def generate_iat_ts() -> int:
    """Get JWT iat field."""
    return timegm(datetime.utcnow().utctimetuple())


def encode(data: ParsedJWTType) -> str:
    """Encode provided data to signed JWT token.

    Args:
        data: JWT data.

    Returns:
        str: JWT string.
    """
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore


def decode(token: str, options: dict[str, bool] = {}) -> ParsedJWTType:
    """Decode JWT token and return its data.

    Args:
        token: JWT token string.

    Raises:
        JWTValidationError: If token is invalid.

    Returns:
        dict: Parsed JWT data.
    """
    try:
        return jwt.decode(  # type: ignore
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options=options,
        )
    except JWTError:
        logger.exception("JWT exception")
        raise JWTValidationError(detail="JWT decode/verification error")


class TokenTypes(Enum):
    """Token types."""

    RefreshToken = 0
    AccessToken = 1
    UUIDReserveToken = 2


class TokenABC(SQLModel, metaclass=ABCMeta):
    """Abstract token model.

    It is intended for refresh JWT tokens. If the `uuid` is in this table,
    then the JWT is valid and can be accepted.
    """

    @abstractmethod
    def issue_refresh_token(self, data: ParsedJWTType = {}) -> str:
        """Issue JWT refresh token.

        Refresh token used for access token issue.

        Examples:
            >>> token = Token()
            >>> token.issue_refresh_token({"some_key": "some_data"})
            "eyJhbGcCJ9.eyJ1aWQiOiI3MzyIn0.w-IX1M5Tmals6HBA"

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
            "eyJhbGcCJ9.eyJ1aWQiOiI3MzyIn0.w-IX1M5Tmals6HBA"

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
            {
              "sub": "1234567890",
              "name": "John Doe",
              "iat": 1516239022
            }

        Args:
            token: JWT token string.

        Raises:
            JWTValidationError: If token is invalid.
        """

    @classmethod
    @abstractmethod
    def verify(cls, parsed: ParsedJWTType, typ: TokenTypes, db: Session) -> None:
        """Verify that token is valid.

        Examples:
            >>> parsed = Token.parse("eyJhbGcCJ9.eyJ1aWQiOiI3MzyIn0.w-IX1M5Tmals6HBA")
            >>> Token.verify(parsed, TokenType.AccessToken, db)

        Args:
            parsed: Parsed JWT token.
            typ: Token type.
            db: Database session.

        Returns:
            None: If token valid and can be accepted.

        Raises:
            JWTValidationError: If token is invalid.
        """

    @classmethod
    @abstractmethod
    def from_str(cls: Type[T], token: str, typ: TokenTypes, db: Session) -> T:
        """Parse, verify and return prepared class.

        Examples:
            >>> token = Token.from_str("eyJhbGcCJ9.eyJ1aWQiOiI3MzyIn0.w-IX1M5Tmals6HBA")
            Token(...)

        Returns:
            TokenABC: Child of TokenABC.

        Raises:
            JWTValidationError: If token invalid.
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
                "iat": generate_iat_ts(),
                "typ": TokenTypes.RefreshToken.value,
                "jti": self.uuid.hex,
                "class": self.__class__.__name__,
            }
        )
        return encode(to_encode)

    def issue_access_token(self, data: ParsedJWTType = {}) -> str:
        to_encode = data.copy()
        to_encode.update(
            {
                "exp": generate_access_token_expire_ts(),
                "iat": generate_iat_ts(),
                "typ": TokenTypes.AccessToken.value,
                "sid": self.uuid.hex,
                "class": self.__class__.__name__,
            }
        )
        return encode(to_encode)

    @classmethod
    def cleanup(cls) -> None:
        with get_engine_session() as db:
            q = db.query(cls).filter(cls.expire_in <= generate_iat_ts())
            count = q.count()
            q.delete()
            logger.info(f"Deleted {count} expired UserTokens.")

    @staticmethod
    def parse(token: str) -> ParsedJWTType:
        return decode(
            token,
            {"require_iat": True, "require_exp": True, "require_sub": True},
        )

    @classmethod
    def verify(cls, parsed: ParsedJWTType, typ: TokenTypes, db: Session) -> None:
        typ_value = parsed.get("typ")
        if typ_value is None:
            raise JWTValidationError("typ field is not provided")
        if typ_value != typ.value:
            raise JWTValidationError(f"{typ.name} token is required")
        if typ == TokenTypes.RefreshToken:
            jti_value = parsed.get("jti")
            if jti_value is None:
                raise JWTValidationError("jti field is not provided")
            if db.query(cls).filter(cls.uuid == parsed["jti"]).first() is None:
                raise JWTRevokedException("JWT not found.")


class UserToken(TokenBase, table=True):
    """User JWT token table."""

    user: UUID = Field(nullable=False, foreign_key="user.uuid")

    def issue_refresh_token(self, data: ParsedJWTType = {}) -> str:
        assert self.user is not None
        data.update({"sub": self.user.hex})
        return super().issue_refresh_token(data)

    def issue_access_token(self, data: ParsedJWTType = {}) -> str:
        assert self.user is not None
        # TODO: add scopes
        data.update({"sub": self.user.hex})
        return super().issue_access_token(data)

    def issue_access_token_user_data(self, db: Session, data: ParsedJWTType = {}) -> str:
        """Issue access token with additional user data, such as `scope`, `email`, `nickname`."""
        assert self.user is not None
        user_model = db.query(User).where(User.uuid == self.user).first()
        assert user_model is not None
        data.update({"nickname": user_model.nickname, "email": user_model.email})
        return self.issue_access_token(data)

    @classmethod
    def verify(cls, parsed: ParsedJWTType, typ: TokenTypes, db: Session) -> None:
        super().verify(parsed, typ, db)
        if typ == TokenTypes.RefreshToken:
            user = db.query(User).filter(User.uuid == parsed["sub"]).first()
            if user is None:
                raise JWTRevokedException("User not found.")
            if user.disabled:
                raise JWTRevokedException("Disabled user.")

    @classmethod
    def from_str(cls: Type[T], token: str, typ: TokenTypes, db: Session) -> T:
        parsed = cls.parse(token)
        cls.verify(parsed, typ, db)
        return cls(
            uuid=parsed.get("jti") if parsed.get("jti") is not None else parsed["sid"],
            expire_in=parsed["exp"],
            user=parsed["sub"],
        )

    @classmethod
    def from_str_access_token(cls: Type[T], token: str) -> T:
        """Parse token, assuming its AccessToken and it doesnt require database connection."""
        return cls.from_str(token, TokenTypes.AccessToken, Session())
