"""Tests for the travels domain: public GET and admin POST/DELETE."""

import uuid

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import text

from src.auth.service import hash_password

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
}


async def _create_test_user(engine, user_id: str, username: str, email: str, password: str) -> None:
    """Create a user directly in the test DB."""
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
        TEST_USER["username"],
        TEST_USER["email"],
        TEST_USER["password"],
    )
    resp = await client.post(
        "/auth/login",
        json={"username": TEST_USER["username"], "password": TEST_USER["password"]},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _auth_headers(token: str) -> dict[str, str]:
    """Return Authorization header dict."""
    return {"Authorization": f"Bearer {token}"}


# ------------------------------------------------------------------
# GET /travels  (public)
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_travels_empty(client: httpx.AsyncClient) -> None:
    """Empty database returns two empty lists."""
    resp = await client.get("/travels")
    assert resp.status_code == 200
    data = resp.json()
    assert data == {"visited": [], "bucketlist": []}


@pytest.mark.asyncio
async def test_get_travels_returns_visited(client: httpx.AsyncClient, test_engine) -> None:
    """Visited countries appear in the visited list."""
    async with test_engine.begin() as conn:
        await conn.execute(
            text(
                "INSERT INTO travel (id, country_code, status) VALUES (gen_random_uuid(), :code, :status)"
            ),
            {"code": "FR", "status": "visited"},
        )
        await conn.commit()

    resp = await client.get("/travels")
    assert resp.status_code == 200
    data = resp.json()
    assert data["visited"] == ["FR"]
    assert data["bucketlist"] == []


@pytest.mark.asyncio
async def test_get_travels_returns_bucketlist(client: httpx.AsyncClient, test_engine) -> None:
    """Bucketlist countries appear in the bucketlist list."""
    async with test_engine.begin() as conn:
        await conn.execute(
            text(
                "INSERT INTO travel (id, country_code, status) VALUES (gen_random_uuid(), :code, :status)"
            ),
            {"code": "JP", "status": "bucketlist"},
        )
        await conn.commit()

    resp = await client.get("/travels")
    assert resp.status_code == 200
    data = resp.json()
    assert data["visited"] == []
    assert data["bucketlist"] == ["JP"]


@pytest.mark.asyncio
async def test_get_travels_sorted(client: httpx.AsyncClient, test_engine) -> None:
    """Country codes are sorted alphabetically within each list."""
    codes = [
        ("US", "visited"),
        ("AU", "bucketlist"),
        ("BR", "visited"),
        ("CA", "bucketlist"),
        ("DE", "visited"),
    ]
    async with test_engine.begin() as conn:
        for code, status_val in codes:
            await conn.execute(
                text(
                    "INSERT INTO travel (id, country_code, status) VALUES (gen_random_uuid(), :code, :status)"
                ),
                {"code": code, "status": status_val},
            )
        await conn.commit()

    resp = await client.get("/travels")
    assert resp.status_code == 200
    data = resp.json()
    assert data["visited"] == ["BR", "DE", "US"]
    assert data["bucketlist"] == ["AU", "CA"]


@pytest.mark.asyncio
async def test_get_travels_no_auth_required(client: httpx.AsyncClient) -> None:
    """Public endpoint works without authentication."""
    resp = await client.get("/travels")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_get_travels_many_countries(client: httpx.AsyncClient, test_engine) -> None:
    """Handles a realistic number of countries."""
    codes = [
        ("US", "visited"),
        ("GB", "visited"),
        ("FR", "visited"),
        ("JP", "bucketlist"),
        ("AU", "bucketlist"),
        ("BR", "bucketlist"),
        ("ZA", "bucketlist"),
    ]
    async with test_engine.begin() as conn:
        for code, status_val in codes:
            await conn.execute(
                text(
                    "INSERT INTO travel (id, country_code, status) VALUES (gen_random_uuid(), :code, :status)"
                ),
                {"code": code, "status": status_val},
            )
        await conn.commit()

    resp = await client.get("/travels")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["visited"]) == 3
    assert len(data["bucketlist"]) == 4


# ------------------------------------------------------------------
# POST /admin/travels  (batch replace)
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_batch_create_empty_lists(client: httpx.AsyncClient, auth_token: str) -> None:
    """Empty lists clear all travels."""
    resp = await client.post(
        "/admin/travels/",
        json={"visited": [], "bucketlist": []},
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data == {"visited": [], "bucketlist": []}


@pytest.mark.asyncio
async def test_batch_create_populates_visited(client: httpx.AsyncClient, auth_token: str) -> None:
    """Visited codes are created with status=visited."""
    resp = await client.post(
        "/admin/travels/",
        json={"visited": ["FR", "DE"], "bucketlist": []},
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert set(data["visited"]) == {"DE", "FR"}
    assert data["bucketlist"] == []


@pytest.mark.asyncio
async def test_batch_create_populates_bucketlist(client: httpx.AsyncClient, auth_token: str) -> None:
    """Bucketlist codes are created with status=bucketlist."""
    resp = await client.post(
        "/admin/travels/",
        json={"visited": [], "bucketlist": ["JP", "AU"]},
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert set(data["bucketlist"]) == {"AU", "JP"}


@pytest.mark.asyncio
async def test_batch_create_both_lists(client: httpx.AsyncClient, auth_token: str) -> None:
    """Both visited and bucketlist populated in one call."""
    resp = await client.post(
        "/admin/travels/",
        json={"visited": ["FR"], "bucketlist": ["JP"]},
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["visited"] == ["FR"]
    assert data["bucketlist"] == ["JP"]


@pytest.mark.asyncio
async def test_batch_create_deduplicates_within_list(client: httpx.AsyncClient, auth_token: str) -> None:
    """Duplicate codes within the same list are deduplicated."""
    resp = await client.post(
        "/admin/travels/",
        json={"visited": ["FR", "FR", "DE"], "bucketlist": []},
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["visited"] == ["DE", "FR"]


@pytest.mark.asyncio
async def test_batch_create_normalises_codes(client: httpx.AsyncClient, auth_token: str) -> None:
    """Codes are uppercased and trimmed."""
    resp = await client.post(
        "/admin/travels/",
        json={"visited": ["  fr  ", "de"], "bucketlist": ["jp"]},
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "FR" in data["visited"]
    assert "DE" in data["visited"]
    assert "JP" in data["bucketlist"]


@pytest.mark.asyncio
async def test_batch_create_ignores_empty_strings(client: httpx.AsyncClient, auth_token: str) -> None:
    """Empty or whitespace-only strings are ignored."""
    resp = await client.post(
        "/admin/travels/",
        json={"visited": ["FR", "", "  ", "DE"], "bucketlist": []},
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["visited"] == ["DE", "FR"]


@pytest.mark.asyncio
async def test_batch_create_replaces_status(client: httpx.AsyncClient, auth_token: str) -> None:
    """Moving a country from visited to bucketlist updates status."""
    await client.post(
        "/admin/travels/",
        json={"visited": ["FR"], "bucketlist": []},
        headers=_auth_headers(auth_token),
    )
    resp = await client.post(
        "/admin/travels/",
        json={"visited": [], "bucketlist": ["FR"]},
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["visited"] == []
    assert data["bucketlist"] == ["FR"]


@pytest.mark.asyncio
async def test_batch_create_removes_stale(client: httpx.AsyncClient, auth_token: str) -> None:
    """Countries not in either list are deleted."""
    await client.post(
        "/admin/travels/",
        json={"visited": ["FR", "DE"], "bucketlist": ["JP"]},
        headers=_auth_headers(auth_token),
    )
    resp = await client.post(
        "/admin/travels/",
        json={"visited": ["FR"], "bucketlist": []},
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["visited"] == ["FR"]
    assert data["bucketlist"] == []


@pytest.mark.asyncio
async def test_batch_create_unauthorized(client: httpx.AsyncClient) -> None:
    """Requires authentication."""
    resp = await client.post("/admin/travels/", json={"visited": ["FR"], "bucketlist": []})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_batch_create_invalid_token(client: httpx.AsyncClient) -> None:
    """Invalid token is rejected."""
    headers = {"Authorization": "Bearer invalid-token"}
    resp = await client.post(
        "/admin/travels/",
        json={"visited": ["FR"], "bucketlist": []},
        headers=headers,
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_batch_create_with_non_standard_code(client: httpx.AsyncClient, auth_token: str) -> None:
    """Non-standard codes are accepted (no validation on code format)."""
    resp = await client.post(
        "/admin/travels/",
        json={"visited": ["XX"], "bucketlist": []},
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["visited"] == ["XX"]


@pytest.mark.asyncio
async def test_batch_create_large_batch(client: httpx.AsyncClient, auth_token: str) -> None:
    """Handles a large batch of countries."""
    # Generate unique 2-char codes: AA, AB, ..., AZ, BA, BB, ...
    all_visited = []
    for i in range(50):
        c1 = chr(65 + i // 26)
        c2 = chr(65 + i % 26)
        all_visited.append(f"{c1}{c2}")
    resp = await client.post(
        "/admin/travels/",
        json={"visited": all_visited, "bucketlist": []},
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert len(data["visited"]) == 50


@pytest.mark.asyncio
async def test_batch_create_multiple_calls_replace_state(
    client: httpx.AsyncClient,
    auth_token: str,
) -> None:
    """Each call fully replaces the previous state."""
    await client.post(
        "/admin/travels/",
        json={"visited": ["FR", "DE"], "bucketlist": ["JP"]},
        headers=_auth_headers(auth_token),
    )
    await client.post(
        "/admin/travels/",
        json={"visited": ["US"], "bucketlist": ["AU", "CA"]},
        headers=_auth_headers(auth_token),
    )
    resp = await client.get("/travels")
    assert resp.status_code == 200
    data = resp.json()
    assert data["visited"] == ["US"]
    assert set(data["bucketlist"]) == {"AU", "CA"}


# ------------------------------------------------------------------
# DELETE /admin/travels/{country_code}
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_travel_success(client: httpx.AsyncClient, auth_token: str) -> None:
    """Deleting an existing travel returns 204."""
    await client.post(
        "/admin/travels/",
        json={"visited": ["FR"], "bucketlist": []},
        headers=_auth_headers(auth_token),
    )
    resp = await client.delete("/admin/travels/FR", headers=_auth_headers(auth_token))
    assert resp.status_code == 204

    # Verify it's gone
    resp = await client.get("/travels")
    assert resp.status_code == 200
    data = resp.json()
    assert data["visited"] == []


@pytest.mark.asyncio
async def test_delete_travel_not_found(client: httpx.AsyncClient, auth_token: str) -> None:
    """Deleting a non-existent travel returns 404."""
    resp = await client.delete("/admin/travels/NR", headers=_auth_headers(auth_token))
    assert resp.status_code == 404
    data = resp.json()
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_delete_travel_unauthorized(client: httpx.AsyncClient) -> None:
    """Requires authentication."""
    resp = await client.delete("/admin/travels/FR")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_delete_travel_invalid_token(client: httpx.AsyncClient) -> None:
    """Invalid token is rejected."""
    headers = {"Authorization": "Bearer invalid-token"}
    resp = await client.delete("/admin/travels/FR", headers=headers)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_delete_travel_case_insensitive(client: httpx.AsyncClient, auth_token: str) -> None:
    """Delete works with lower-case code (normalised to upper)."""
    await client.post(
        "/admin/travels/",
        json={"visited": ["FR"], "bucketlist": []},
        headers=_auth_headers(auth_token),
    )
    resp = await client.delete("/admin/travels/fr", headers=_auth_headers(auth_token))
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_travel_with_whitespace(client: httpx.AsyncClient, auth_token: str) -> None:
    """Whitespace around the code is trimmed."""
    await client.post(
        "/admin/travels/",
        json={"visited": ["FR"], "bucketlist": []},
        headers=_auth_headers(auth_token),
    )
    resp = await client.delete("/admin/travels/  FR  ", headers=_auth_headers(auth_token))
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_travel_does_not_affect_other_status(
    client: httpx.AsyncClient,
    auth_token: str,
) -> None:
    """Deleting a bucketlist country doesn't affect visited."""
    await client.post(
        "/admin/travels/",
        json={"visited": ["US"], "bucketlist": ["JP"]},
        headers=_auth_headers(auth_token),
    )
    await client.delete("/admin/travels/JP", headers=_auth_headers(auth_token))

    resp = await client.get("/travels")
    assert resp.status_code == 200
    data = resp.json()
    assert data["visited"] == ["US"]
    assert data["bucketlist"] == []


# ------------------------------------------------------------------
# Integration: full lifecycle
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_full_lifecycle(client: httpx.AsyncClient, auth_token: str) -> None:
    """Create → update → delete lifecycle."""
    # Create
    resp = await client.post(
        "/admin/travels/",
        json={"visited": ["FR", "DE"], "bucketlist": ["JP"]},
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 201

    # Update: move FR to bucketlist, add US
    resp = await client.post(
        "/admin/travels/",
        json={"visited": ["US", "DE"], "bucketlist": ["JP", "FR"]},
        headers=_auth_headers(auth_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert set(data["visited"]) == {"DE", "US"}
    assert set(data["bucketlist"]) == {"FR", "JP"}

    # Delete
    await client.delete("/admin/travels/FR", headers=_auth_headers(auth_token))

    # Verify
    resp = await client.get("/travels")
    assert resp.status_code == 200
    data = resp.json()
    assert set(data["visited"]) == {"DE", "US"}
    assert data["bucketlist"] == ["JP"]
