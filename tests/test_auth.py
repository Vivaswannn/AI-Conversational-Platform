# tests/test_auth.py
import os
import pytest
from pydantic import ValidationError

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-32chars!!")


def test_register_request_validation():
    from app.schemas.auth import RegisterRequest
    req = RegisterRequest(email="user@example.com", password="secret123")
    assert req.email == "user@example.com"


def test_register_request_rejects_invalid_email():
    from app.schemas.auth import RegisterRequest
    with pytest.raises(ValidationError):
        RegisterRequest(email="not-an-email", password="secret123")


def test_register_request_rejects_short_password():
    from app.schemas.auth import RegisterRequest
    with pytest.raises(ValidationError):
        RegisterRequest(email="user@example.com", password="short")


def test_login_request_rejects_invalid_email():
    from app.schemas.auth import LoginRequest
    with pytest.raises(ValidationError):
        LoginRequest(email="not-an-email", password="password123")


def test_token_response_default_type():
    from app.schemas.auth import TokenResponse
    t = TokenResponse(access_token="some-jwt-token")
    assert t.token_type == "bearer"


def test_user_out_from_attributes():
    from app.schemas.auth import UserOut
    from datetime import datetime, timezone

    class FakeUser:
        id = "123e4567-e89b-12d3-a456-426614174000"
        email = "user@example.com"
        is_active = True
        created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)

    user_out = UserOut.model_validate(FakeUser())
    assert user_out.email == "user@example.com"
    assert user_out.is_active is True
    assert user_out.token_type if hasattr(user_out, "token_type") else True


def test_hash_and_verify_password():
    from app.services.auth_service import hash_password, verify_password
    hashed = hash_password("mypassword")
    assert verify_password("mypassword", hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_and_decode_token():
    from app.services.auth_service import create_access_token, decode_access_token
    from datetime import datetime, timezone
    token = create_access_token({"sub": "user-id-123"})
    payload = decode_access_token(token)
    assert payload["sub"] == "user-id-123"
    assert "exp" in payload
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()


def test_decode_invalid_token_raises():
    from app.services.auth_service import decode_access_token
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token("not.a.valid.token")
    assert exc_info.value.status_code == 401


def test_decode_expired_token_raises():
    from app.services.auth_service import decode_access_token
    from app.config import get_settings
    from jose import jwt
    from datetime import datetime, timedelta, timezone
    from fastapi import HTTPException
    settings = get_settings()
    expired_token = jwt.encode(
        {"sub": "user-123", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(expired_token)
    assert exc_info.value.status_code == 401


# --- Integration tests ---

@pytest.mark.asyncio
async def test_register_creates_user(client):
    resp = await client.post("/auth/register", json={
        "email": "new@example.com", "password": "password123"
    })
    assert resp.status_code == 201
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_register_duplicate_email_rejected(client):
    body = {"email": "dup@example.com", "password": "password123"}
    await client.post("/auth/register", json=body)
    resp = await client.post("/auth/register", json=body)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/auth/register", json={"email": "login@example.com", "password": "password123"})
    resp = await client.post("/auth/login", json={"email": "login@example.com", "password": "password123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/auth/register", json={"email": "user2@example.com", "password": "password123"})
    resp = await client.post("/auth/login", json={"email": "user2@example.com", "password": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_auth(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_user(client, registered_user):
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {registered_user['token']}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == registered_user["email"]
