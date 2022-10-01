from time import time
from uuid import uuid4

from app.database import get_engine_session
from app.models import TokenTypes, User, UserToken


def test_issue_refresh_token() -> None:
    uuid = uuid4()
    token_uuid = uuid4()
    user = User(email=uuid.hex + "@bar.com", nickname=uuid.hex, uuid=uuid)
    usertoken = UserToken(user=user.uuid, uuid=token_uuid)
    token = usertoken.issue_refresh_token()
    parsed = UserToken.parse(token)
    assert parsed["typ"] == TokenTypes.RefreshToken.value
    assert parsed["exp"] > time()  # type: ignore
    assert parsed["iat"] <= time()  # type: ignore
    assert parsed["class"] == "UserToken"
    assert parsed["sub"] == uuid.hex
    with get_engine_session() as db:
        db.add(user)
        db.commit()
        db.add(usertoken)
        db.commit()
        UserToken.verify(parsed, TokenTypes.RefreshToken, db)
        token_from_str = UserToken.from_str(token, TokenTypes.RefreshToken, db)
    assert token_from_str.user == uuid


def test_issue_access_token() -> None:
    uuid = uuid4()
    token_uuid = uuid4()
    user = User(email=uuid.hex + "@bar.com", nickname=uuid.hex, uuid=uuid)
    usertoken = UserToken(user=user.uuid, uuid=token_uuid)
    token = usertoken.issue_access_token()
    parsed = UserToken.parse(token)
    assert parsed["typ"] == TokenTypes.AccessToken.value
    assert parsed["exp"] > time()  # type: ignore
    assert parsed["iat"] <= time()  # type: ignore
    assert parsed["class"] == "UserToken"
    assert parsed["sub"] == uuid.hex
    with get_engine_session() as db:
        db.add(user)
        db.commit()
        db.add(usertoken)
        db.commit()
        UserToken.verify(parsed, TokenTypes.AccessToken, db)
        token_from_str = UserToken.from_str(token, TokenTypes.AccessToken, db)
    assert token_from_str.user == uuid
