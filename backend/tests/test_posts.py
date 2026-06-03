import uuid

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.auth.service import hash_password
from src.config import settings

# --- Auth helpers ---

TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
}


async def _create_test_user(db_url: str, user_id: str, username: str, email: str, password: str) -> None:
    """Create a user directly in the DB using a fresh engine."""
    eng = create_async_engine(url=db_url, pool_pre_ping=True)
    try:
        async with eng.connect() as conn:
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
    except RuntimeError:
        # Event loop may be closed during test teardown; ignore dispose errors
        pass
    else:
        try:
            await eng.dispose()
        except RuntimeError:
            # Loop already closed during test cleanup
            pass


async def get_auth_header(client: httpx.AsyncClient) -> dict[str, str]:
    """Create a user via DB and log in to get the Authorization header."""
    await _create_test_user(
        settings.DATABASE_URL,
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        TEST_USER["username"],
        TEST_USER["email"],
        TEST_USER["password"],
    )

    login_resp = await client.post(
        "/auth/login",
        json={"username": TEST_USER["username"], "password": TEST_USER["password"]},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# --- Helpers ---


def make_post_data(
    title: str = "Test Post",
    slug: str = "test-post",
    content: dict | None = None,
    excerpt: str | None = None,
) -> dict:
    data: dict = {
        "title": title,
        "slug": slug,
        "content": content or {"body": "Hello world"},
    }
    if excerpt is not None:
        data["excerpt"] = excerpt
    return data


# --- GET /posts (list, public, paginated) ---


@pytest.mark.asyncio
async def test_list_posts_empty(client: httpx.AsyncClient) -> None:
    resp = await client.get("/posts/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_posts_returns_created(client: httpx.AsyncClient) -> None:
    headers = await get_auth_header(client)
    create_resp = await client.post("/admin/posts/", json=make_post_data(), headers=headers)
    assert create_resp.status_code == 201

    resp = await client.get("/posts/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Test Post"


@pytest.mark.asyncio
async def test_list_posts_returns_all(client: httpx.AsyncClient) -> None:
    headers = await get_auth_header(client)
    for slug in ["alpha", "beta", "gamma"]:
        await client.post("/admin/posts/", json=make_post_data(slug=slug), headers=headers)

    resp = await client.get("/posts/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 3
    assert {p["slug"] for p in data["items"]} == {"alpha", "beta", "gamma"}


# --- GET /posts/{post_id} ---


@pytest.mark.asyncio
async def test_get_post_by_id(client: httpx.AsyncClient) -> None:
    headers = await get_auth_header(client)
    create_resp = await client.post("/admin/posts/", json=make_post_data(), headers=headers)
    post = create_resp.json()

    resp = await client.get(f"/posts/{post['id']}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Test Post"


@pytest.mark.asyncio
async def test_get_post_not_found(client: httpx.AsyncClient) -> None:
    resp = await client.get(f"/posts/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_post_invalid_uuid(client: httpx.AsyncClient) -> None:
    resp = await client.get("/posts/not-a-uuid")
    assert resp.status_code == 422  # FastAPI validation error


# --- POST /admin/posts (create) ---


@pytest.mark.asyncio
async def test_create_post(client: httpx.AsyncClient) -> None:
    headers = await get_auth_header(client)
    resp = await client.post("/admin/posts/", json=make_post_data(), headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Post"
    assert data["slug"] == "test-post"
    assert data["content"] == {"body": "Hello world"}
    assert data["excerpt"] is None
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_post_with_excerpt(client: httpx.AsyncClient) -> None:
    headers = await get_auth_header(client)
    resp = await client.post(
        "/admin/posts/",
        json=make_post_data(excerpt="A short excerpt"),
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["excerpt"] == "A short excerpt"


@pytest.mark.asyncio
async def test_create_post_duplicate_slug(client: httpx.AsyncClient) -> None:
    headers = await get_auth_header(client)
    payload = make_post_data(slug="unique-slug")
    resp1 = await client.post("/admin/posts/", json=payload, headers=headers)
    assert resp1.status_code == 201

    resp2 = await client.post("/admin/posts/", json=payload, headers=headers)
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_create_post_missing_title(client: httpx.AsyncClient) -> None:
    headers = await get_auth_header(client)
    payload = make_post_data()
    del payload["title"]
    resp = await client.post("/admin/posts/", json=payload, headers=headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_post_invalid_slug_format(client: httpx.AsyncClient) -> None:
    headers = await get_auth_header(client)
    resp = await client.post(
        "/admin/posts/",
        json=make_post_data(slug="INVALID SLUG!"),
        headers=headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_post_missing_content(client: httpx.AsyncClient) -> None:
    headers = await get_auth_header(client)
    payload = make_post_data()
    del payload["content"]
    resp = await client.post("/admin/posts/", json=payload, headers=headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_post_unauthorized(client: httpx.AsyncClient) -> None:
    resp = await client.post("/admin/posts/", json=make_post_data())
    assert resp.status_code == 401


# --- PUT /admin/posts/{post_id} (update) ---


@pytest.mark.asyncio
async def test_update_post(client: httpx.AsyncClient) -> None:
    headers = await get_auth_header(client)
    create_resp = await client.post("/admin/posts/", json=make_post_data(), headers=headers)
    post = create_resp.json()

    resp = await client.put(
        f"/admin/posts/{post['id']}",
        json={"title": "Updated Title"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated Title"
    assert data["slug"] == "test-post"  # unchanged


@pytest.mark.asyncio
async def test_update_post_multiple_fields(client: httpx.AsyncClient) -> None:
    headers = await get_auth_header(client)
    create_resp = await client.post("/admin/posts/", json=make_post_data(), headers=headers)
    post = create_resp.json()

    resp = await client.put(
        f"/admin/posts/{post['id']}",
        json={"title": "New Title", "slug": "new-slug", "excerpt": "Updated excerpt"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "New Title"
    assert data["slug"] == "new-slug"
    assert data["excerpt"] == "Updated excerpt"


@pytest.mark.asyncio
async def test_update_post_not_found(client: httpx.AsyncClient) -> None:
    headers = await get_auth_header(client)
    resp = await client.put(
        f"/admin/posts/{uuid.uuid4()}",
        json={"title": "Nope"},
        headers=headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_post_slug_conflict(client: httpx.AsyncClient) -> None:
    headers = await get_auth_header(client)
    await client.post("/admin/posts/", json=make_post_data(slug="first"), headers=headers)
    create_resp = await client.post(
        "/admin/posts/",
        json=make_post_data(slug="second"),
        headers=headers,
    )
    post = create_resp.json()

    resp = await client.put(
        f"/admin/posts/{post['id']}",
        json={"slug": "first"},
        headers=headers,
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_update_post_unauthorized(client: httpx.AsyncClient) -> None:
    resp = await client.put(f"/admin/posts/{uuid.uuid4()}", json={"title": "Nope"})
    assert resp.status_code == 401


# --- DELETE /admin/posts/{post_id} ---


@pytest.mark.asyncio
async def test_delete_post(client: httpx.AsyncClient) -> None:
    headers = await get_auth_header(client)
    create_resp = await client.post("/admin/posts/", json=make_post_data(), headers=headers)
    post = create_resp.json()

    resp = await client.delete(f"/admin/posts/{post['id']}", headers=headers)
    assert resp.status_code == 204

    # Verify it's gone
    resp = await client.get(f"/admin/posts/{post['id']}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_post_not_found(client: httpx.AsyncClient) -> None:
    headers = await get_auth_header(client)
    resp = await client.delete(f"/admin/posts/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_post_unauthorized(client: httpx.AsyncClient) -> None:
    resp = await client.delete(f"/admin/posts/{uuid.uuid4()}")
    assert resp.status_code == 401
