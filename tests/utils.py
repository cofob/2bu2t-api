from uuid import UUID, uuid4

from app.models.user import User


def get_user(uuid: UUID = uuid4()) -> User:
    user = User(email=uuid.hex + "@bar.com", nickname=uuid.hex[:6], uuid=uuid, password=uuid.hex)
    return user
