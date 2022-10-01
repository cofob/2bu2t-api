from fastapi.testclient import TestClient

from app import app
from app.models.token import decode

client = TestClient(app)


def test_uuid_token() -> None:
    response = client.get("/authorization/signup/reserve_uuid")
    assert response.status_code == 200
    decode(response.json())
