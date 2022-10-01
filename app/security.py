"""Module containing authentication-related functions."""

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlmodel import Session

from app.exceptions import InvalidPasswordException, UserNotFoundException
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="authorization/login/get_token_pair")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare plain password and password hash.

    Args:
        plain_password: Plain password string.
        hashed_password: Hashed password string.

    Returns:
        bool: `True` if the password matched the hash, else `False`.
    """
    return pwd_context.verify(plain_password, hashed_password)  # type: ignore


def get_password_hash(password: str) -> str:
    """Compute pasword hash from plain password string.

    Args:
        password: Plain password string.

    Returns:
        str: Hashed password.
    """
    return pwd_context.hash(password)  # type: ignore


def authenticate_user(db: Session, nickname: str, password: str) -> User:
    """Verify nickname and password.

    Args:
        db: Database session.
        nickname: User nickname.
        password: Plain password.

    Raises:
        UserNotFoundException: If nickname not found in database.
        InvalidPasswordException: If password invalid.

    Returns:
        User: If everything ok.
    """
    user: User | None = db.query(User).where(User.nickname == nickname).first()
    if not user:
        raise UserNotFoundException()
    if not verify_password(password, user.password):
        raise InvalidPasswordException()
    return user
