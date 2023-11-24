import json

import pytest
from aioresponses import aioresponses

from src.auth.routes import AUTHENTICATION_PREFIX


@pytest.mark.usefixtures("mock_fetch_service")
async def test_success_login(client, create_user_data, token_pair):
    response = client.post(f"{AUTHENTICATION_PREFIX}/login", json=create_user_data.model_dump())

    assert response.status_code == 200

    response_data = response.json()
    assert response_data == token_pair.model_dump()

    assert "access_token" in response.cookies
    assert response.cookies["access_token"] == token_pair.access_token

    assert "refresh_token" in response.cookies
    assert response.cookies["refresh_token"] == token_pair.refresh_token


async def test_login_invalid_input_user_data(client):
    user_data = {"username": "mimimimi"}
    response = client.post(f"{AUTHENTICATION_PREFIX}/login", json=user_data)

    assert response.status_code == 422

    response_data = response.json()
    assert response_data == {
        "detail": [
            {
                "input": {"username": "mimimimi"},
                "loc": ["body", "password"],
                "msg": "Field required",
                "type": "missing",
                "url": "https://errors.pydantic.dev/2.5/v/missing",
            }
        ]
    }


async def test_login_with_auth_service_unavailable(client, create_user_data):
    response = client.post(f"{AUTHENTICATION_PREFIX}/login", json=create_user_data.model_dump())

    assert response.status_code == 503
    assert response.json() == {"detail": "Auth service unavailable right now"}


@pytest.mark.parametrize(
    "status_code, error_detail",
    [
        (
            403,
            {"detail": "Invalid credentials"},
        ),
        (
            404,
            {"detail": "can't find user"},
        ),
    ],
)
async def test_login_with_failed_authentication(status_code, error_detail, client, create_user_data, auth_settings):
    url = auth_settings.authentication_url
    with aioresponses() as mock_aiohttp:
        mock_aiohttp.post(url, status=status_code, body=json.dumps(error_detail))

        response = client.post(f"{AUTHENTICATION_PREFIX}/login", json=create_user_data.model_dump())
        assert response.status_code == status_code
        assert response.json() == error_detail


@pytest.mark.usefixtures("mock_fetch_service", "wrong_authentication")
async def test_success_refresh(client, create_user_data, token_pair):
    response = client.post(f"{AUTHENTICATION_PREFIX}/refresh_token")

    assert response.status_code == 200

    response_data = response.json()
    assert response_data == token_pair.model_dump()

    assert "access_token" in response.cookies
    assert response.cookies["access_token"] == token_pair.access_token

    assert "refresh_token" in response.cookies
    assert response.cookies["refresh_token"] == token_pair.refresh_token


@pytest.mark.usefixtures("authenticate_user")
async def test_refresh_with_auth_service_unavailable(client, create_user_data):
    response = client.post(f"{AUTHENTICATION_PREFIX}/refresh_token")

    assert response.status_code == 503
    assert response.json() == {"detail": "Auth service unavailable right now"}


@pytest.mark.usefixtures("mock_fetch_service")
async def test_refresh_not_authenticated(client, create_user_data):
    response = client.post(f"{AUTHENTICATION_PREFIX}/refresh_token")

    assert response.status_code == 403
    assert response.json() == {"detail": "Could not valid credentials"}


@pytest.mark.parametrize(
    "status_code, error_detail",
    [
        (
            403,
            {"detail": "Could not valid credentials"},
        ),
        (
            404,
            {"detail": "can't find user"},
        ),
    ],
)
@pytest.mark.usefixtures("authenticate_user")
async def test_refresh_with_failed_authentication(status_code, error_detail, client, auth_settings):
    url = auth_settings.refresh_token_url
    with aioresponses() as mock_aiohttp:
        mock_aiohttp.post(url, status=status_code, body=json.dumps(error_detail))

        response = client.post(f"{AUTHENTICATION_PREFIX}/refresh_token")
        assert response.status_code == status_code
        assert response.json() == error_detail
