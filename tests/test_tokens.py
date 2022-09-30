from time import time
from uuid import uuid4

from app.database import get_engine_session
from app.models import TokenTypes, User, UserToken


def test_issue_refresh_token() -> None:
    uuid = uuid4()
    user = User(email="foo", nickname="bar", uuid=uuid)
    usertoken = UserToken(user=user.uuid)
    token = usertoken.issue_refresh_token()
    parsed = UserToken.parse(token)
    assert parsed["typ"] == TokenTypes.RefreshToken.value
    assert parsed["exp"] > time()  # type: ignore
    assert parsed["iat"] <= time()  # type: ignore
    assert parsed["class"] == "UserToken"
    assert parsed["sub"] == str(uuid)
    with get_engine_session() as db:
        db.add(user)
        db.commit()
        db.add(usertoken)
        db.commit()
        UserToken.verify(parsed, TokenTypes.RefreshToken, db)


def test_issue_access_token() -> None:
    uuid = uuid4()
    user = UserToken(user=uuid)
    token = user.issue_access_token()
    parsed = UserToken.parse(token)
    assert parsed["typ"] == TokenTypes.AccessToken.value
    assert parsed["exp"] > time()  # type: ignore
    assert parsed["iat"] <= time()  # type: ignore
    assert parsed["class"] == "UserToken"
    assert parsed["sub"] == str(uuid)
    UserToken.verify(parsed, TokenTypes.AccessToken)
