import pytest
from fastapi.testclient import TestClient

from app.config.config import Config
from app.infra.dto.user.user_dto import UserDTO
from app.main import journeyLingua
from tests.conftest import TEST_USER_EMAIL, TEST_USER_PHONE

client = TestClient(journeyLingua)


@pytest.mark.parametrize(
    "test_create_user",
    [
        {"email": TEST_USER_EMAIL, "is_email_verified": True},
        {"email": TEST_USER_EMAIL, "is_email_verified": False},
    ],
    indirect=["test_create_user"],
)
@pytest.mark.asyncio
async def test_login_by_email(test_create_user, async_client, redis):
    user: UserDTO = test_create_user
    response = await async_client.post(
        "/auth/login",
        json={
            "email": user.email,
            "password": "password",
            "login_type": 1,
            "client_id": Config.CLIENT_ID,
            "client_secret": Config.CLIENT_SECRET,
        },
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["data"]["access_token"] is not None
    assert response_json["data"]["token_type"] == "bearer"
    if user.is_email_verified:
        assert response_json["data"]["is_user_verified"] is True
    else:
        assert response_json["data"]["is_user_verified"] is False
    assert int((await redis.get(f'user_session_token:{response_json["data"]["access_token"]}'))) == user.id


@pytest.mark.parametrize(
    "test_create_user",
    [
        {"phone": TEST_USER_PHONE, "is_phone_verified": True},
        {"phone": TEST_USER_PHONE, "is_phone_verified": False},
    ],
    indirect=["test_create_user"],
)
@pytest.mark.asyncio
async def test_login_by_phone(test_create_user, async_client, redis):
    user: UserDTO = test_create_user
    response = await async_client.post(
        "/auth/login",
        json={
            "phone": user.phone,
            "password": "password",
            "login_type": 2,
            "client_id": Config.CLIENT_ID,
            "client_secret": Config.CLIENT_SECRET,
        },
    )

    assert response.status_code == 200

    response_json = response.json()
    assert response_json["data"]["access_token"] is not None
    assert response_json["data"]["token_type"] == "bearer"
    if user.is_phone_verified:
        assert response_json["data"]["is_user_verified"] is True
    else:
        assert response_json["data"]["is_user_verified"] is False
    assert int((await redis.get(f'user_session_token:{response_json["data"]["access_token"]}'))) == user.id
