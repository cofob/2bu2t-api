"""Authorization router."""

from calendar import timegm
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from fastapi import APIRouter, Body, Depends, Query, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import Session

from app.exceptions import JWTValidationError, UserNotFoundException
from app.models.user import User, UserCreate

from ..app import limiter
from ..dependencies import get_session
from ..models import token
from ..security import authenticate_user, get_password_hash

router: APIRouter = APIRouter(prefix="/authorization", tags=["authorization"])


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshToken(BaseModel):
    refresh_token: str
    token_type: str = "bearer"


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegistrationDone(BaseModel):
    pair: TokenPair
    uuid: UUID


@router.post("/signup/", response_model=RegistrationDone)
@limiter.limit("10/minute")
async def signup(
    request: Request,
    db: Session = Depends(get_session),
    user: UserCreate = Body(),
    uuid_token: str = Body(description="Answer from `reserve_uuid` endpoint."),
) -> RegistrationDone:
    """Register account and return token pair.

    **PASSWORD MUST BE HASHED WITH `PBKDF2` WITH `UUID` SALT!**
    """
    parsed = token.decode(uuid_token)
    if parsed["typ"] != token.TokenTypes.UUIDReserveToken.value:
        raise JWTValidationError("UUIDReserveToken expected")
    new_user = User(uuid=parsed["sub"], **user.dict())
    new_user.password = get_password_hash(user.password)
    db.add(new_user)
    db.commit()
    usertoken = token.UserToken(user=new_user.uuid)
    db.add(usertoken)
    db.commit()
    return RegistrationDone(
        uuid=new_user.uuid,
        pair=TokenPair(
            access_token=usertoken.issue_access_token(),
            refresh_token=usertoken.issue_refresh_token(),
        ),
    )


@router.get("/signup/reserve_uuid", response_model=str)
@limiter.limit("2/minute")
async def reserve_uuid(request: Request) -> str:
    """Reserve a `UUID` for registration.

    This `UUID` is used as a salt for the password afterwards, so we
    need to get it beforehand. A `JWT` token will be sent in response,
    confirming the reservation for this `UUID` for 10 minutes, and
    the `UUID` itself.
    """
    return token.encode(
        {
            "typ": token.TokenTypes.UUIDReserveToken.value,
            "exp": timegm((datetime.utcnow() + timedelta(minutes=10)).utctimetuple()),
            "sub": uuid4().hex,
        }
    )


@router.post("/login/", response_model=TokenPair)
@limiter.limit("2/minute")
async def login(
    request: Request,
    db: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> TokenPair:
    """Authenticate and return token pair."""
    user = authenticate_user(db, form_data.username, form_data.password)
    usertoken = token.UserToken(user=user.uuid)
    db.add(usertoken)
    db.commit()
    return TokenPair(
        access_token=usertoken.issue_access_token(), refresh_token=usertoken.issue_refresh_token()
    )


@router.post("/login/get_access_token", response_model=AccessToken)
@limiter.limit("2/minute")
async def get_access_token(
    request: Request, db: Session = Depends(get_session), refresh_token: str = Body(embed=True)
) -> AccessToken:
    """Get access token by refresh token."""
    usertoken = token.UserToken.from_str(refresh_token, token.TokenTypes.RefreshToken, db)
    return AccessToken(access_token=usertoken.issue_access_token())


@router.get("/login/get_uuid", response_model=UUID)
async def get_uuid_by_nickname(
    db: Session = Depends(get_session), nickname: str = Query(max_length=16)
) -> UUID:
    """Get UUID by user nickname."""
    user: User | None = db.query(User).where(User.nickname == nickname).first()
    if user is None:
        raise UserNotFoundException()
    return user.uuid
