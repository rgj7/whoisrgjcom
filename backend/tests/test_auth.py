"""Tests for the auth domain: /auth/me and /auth/login."""

import uuid

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import text

from src.auth.service import hash_password

# --- Helpers ---

VALID_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
}


async def _create_test_user(
    engine,
    user_id: str,
    username: str,
    email: str,
    password: str,
) -> None:
    """Create a test user in the database using a shared engine."""
    async with engine.connect() as conn:
        await conn.execute(
            text(
                'INSERT INTO "user" (id, username, email, hashed_password, created_at) '
                "VALUES (:id, :username, :email, :hashed_password, NOW())"
            ),
            {
                "id": user_id,
                "username": username,
                "email": email,
                "hashed_password": hash_password(password),
            },
        )
        await conn.commit()


@pytest_asyncio.fixture
async def auth_token(client: httpx.AsyncClient, test_engine) -> str:
    """Create a user via the DB and return an auth token."""
    user_id = str(uuid.uuid4())
    await _create_test_user(
        test_engine,
        user_id,
        VALID_USER["username"],
        VALID_USER["email"],
        VALID_USER["password"],
    )

    login_resp = await client.post(
        "/auth/login",
        json={"username": VALID_USER["username"], "password": VALID_USER["password"]},
    )
    assert login_resp.status_code == 200
    return login_resp.json()["access_token"]


async def _login_as(client: httpx.AsyncClient, username: str, password: str) -> str:
    """Log in and return the access token (caller must ensure user exists)."""
    resp = await client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


# ------------------------------------------------------------------
# GET /auth/me
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_me_returns_user_info(client: httpx.AsyncClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}
    resp = await client.get("/auth/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data
    assert "is_superuser" not in data


@pytest.mark.asyncio
async def test_me_unauthorized(client: httpx.AsyncClient) -> None:
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_invalid_token(client: httpx.AsyncClient) -> None:
    headers = {"Authorization": "Bearer invalid-token"}
    resp = await client.get("/auth/me", headers=headers)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_expired_token(client: httpx.AsyncClient, test_engine) -> None:
    """A token with 0-minute expiry should be rejected."""
    from src.auth.dependencies import create_access_token

    await _create_test_user(
        test_engine,
        str(uuid.uuid4()),
        "shortlived",
        "short@lived.com",
        "somepassword",
    )
    token = create_access_token("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", minutes=0)

    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.get("/auth/me", headers=headers)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_cross_user_token(client: httpx.AsyncClient, test_engine) -> None:
    """Any valid token should work — no ownership checks on /me."""
    await _create_test_user(
        test_engine,
        str(uuid.uuid4()),
        "otheruser",
        "other@example.com",
        "correctpassword",
    )
    other_token = await _login_as(client, "otheruser", "correctpassword")

    headers = {"Authorization": f"Bearer {other_token}"}
    resp = await client.get("/auth/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "otheruser"


@pytest.mark.asyncio
async def test_me_missing_bearer_prefix(client: httpx.AsyncClient, auth_token: str) -> None:
    """Token without 'Bearer ' prefix should be rejected."""
    headers = {"Authorization": auth_token}
    resp = await client.get("/auth/me", headers=headers)
    assert resp.status_code == 401


# ------------------------------------------------------------------
# POST /auth/login
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_success(client: httpx.AsyncClient, auth_token: str) -> None:
    resp = await client.post(
        "/auth/login",
        json={"username": VALID_USER["username"], "password": VALID_USER["password"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_returns_unique_token(client: httpx.AsyncClient, test_engine) -> None:
    """Each login call should produce a distinct token."""
    await _create_test_user(
        test_engine,
        str(uuid.uuid4()),
        VALID_USER["username"],
        VALID_USER["email"],
        VALID_USER["password"],
    )
    resp1 = await client.post(
        "/auth/login",
        json={"username": VALID_USER["username"], "password": VALID_USER["password"]},
    )
    resp2 = await client.post(
        "/auth/login",
        json={"username": VALID_USER["username"], "password": VALID_USER["password"]},
    )
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp1.json()["access_token"] != resp2.json()["access_token"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: httpx.AsyncClient, test_engine) -> None:
    await _create_test_user(
        test_engine,
        str(uuid.uuid4()),
        "otheruser",
        "other@example.com",
        "correctpassword",
    )

    resp = await client.post(
        "/auth/login",
        json={"username": "otheruser", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: httpx.AsyncClient) -> None:
    resp = await client.post(
        "/auth/login",
        json={"username": "nobody", "password": "password123"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_missing_username(client: httpx.AsyncClient) -> None:
    resp = await client.post("/auth/login", json={"password": "password123"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_missing_password(client: httpx.AsyncClient) -> None:
    resp = await client.post("/auth/login", json={"username": "testuser"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_empty_body(client: httpx.AsyncClient) -> None:
    resp = await client.post("/auth/login", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_whitespace_username(client: httpx.AsyncClient, test_engine) -> None:
    await _create_test_user(
        test_engine,
        str(uuid.uuid4()),
        VALID_USER["username"],
        VALID_USER["email"],
        VALID_USER["password"],
    )
    resp = await client.post(
        "/auth/login",
        json={"username": "   ", "password": VALID_USER["password"]},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_extra_fields_ignored(client: httpx.AsyncClient, test_engine) -> None:
    """Extra fields in the request body should be silently ignored."""
    await _create_test_user(
        test_engine,
        str(uuid.uuid4()),
        VALID_USER["username"],
        VALID_USER["email"],
        VALID_USER["password"],
    )
    resp = await client.post(
        "/auth/login",
        json={
            "username": VALID_USER["username"],
            "password": VALID_USER["password"],
            "extra": "ignored",
        },
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_non_json_content_type(client: httpx.AsyncClient) -> None:
    """Request without JSON content-type should be rejected by FastAPI."""
    resp = await client.post(
        "/auth/login",
        content=b'{"username":"testuser","password":"password123"}',
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 422
