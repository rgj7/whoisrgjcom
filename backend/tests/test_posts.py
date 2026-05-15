import uuid

import pytest
import pytest_asyncio
from collections.abc import AsyncGenerator

from httpx import AsyncClient, ASGITransport
from sqlalchemy import text

from src.database import async_session
from src.main import app


@pytest_asyncio.fixture(autouse=True)
async def clean_db() -> None:
    """Delete all posts before each test."""
    async with async_session() as session:
        await session.execute(text("DELETE FROM post"))
        await session.commit()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# --- Helpers ---


def make_post_data(
    title: str = "Test Post",
    slug: str = "test-post",
    content: str = "Hello world",
    excerpt: str | None = None,
) -> dict:
    data: dict = {
        "title": title,
        "slug": slug,
        "content": content,
    }
    if excerpt is not None:
        data["excerpt"] = excerpt
    return data


# --- GET /posts (list) ---


@pytest.mark.asyncio
async def test_list_posts_empty(client: AsyncClient) -> None:
    resp = await client.get("/posts/")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_posts_returns_created(client: AsyncClient) -> None:
    create_resp = await client.post("/posts/", json=make_post_data())
    assert create_resp.status_code == 201

    resp = await client.get("/posts/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Post"


@pytest.mark.asyncio
async def test_list_posts_returns_all(client: AsyncClient) -> None:
    for slug in ["alpha", "beta", "gamma"]:
        await client.post("/posts/", json=make_post_data(slug=slug))

    resp = await client.get("/posts/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert {p["slug"] for p in data} == {"alpha", "beta", "gamma"}


# --- GET /posts/{post_id} ---


@pytest.mark.asyncio
async def test_get_post_by_id(client: AsyncClient) -> None:
    create_resp = await client.post("/posts/", json=make_post_data())
    post = create_resp.json()

    resp = await client.get(f"/posts/{post['id']}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Test Post"


@pytest.mark.asyncio
async def test_get_post_not_found(client: AsyncClient) -> None:
    resp = await client.get(f"/posts/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_post_invalid_uuid(client: AsyncClient) -> None:
    resp = await client.get("/posts/not-a-uuid")
    assert resp.status_code == 422  # FastAPI validation error


# --- POST /posts (create) ---


@pytest.mark.asyncio
async def test_create_post(client: AsyncClient) -> None:
    resp = await client.post("/posts/", json=make_post_data())
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Post"
    assert data["slug"] == "test-post"
    assert data["content"] == "Hello world"
    assert data["excerpt"] is None
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_post_with_excerpt(client: AsyncClient) -> None:
    resp = await client.post("/posts/", json=make_post_data(excerpt="A short excerpt"))
    assert resp.status_code == 201
    assert resp.json()["excerpt"] == "A short excerpt"


@pytest.mark.asyncio
async def test_create_post_duplicate_slug(client: AsyncClient) -> None:
    payload = make_post_data(slug="unique-slug")
    resp1 = await client.post("/posts/", json=payload)
    assert resp1.status_code == 201

    resp2 = await client.post("/posts/", json=payload)
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_create_post_missing_title(client: AsyncClient) -> None:
    payload = make_post_data()
    del payload["title"]
    resp = await client.post("/posts/", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_post_invalid_slug_format(client: AsyncClient) -> None:
    resp = await client.post("/posts/", json=make_post_data(slug="INVALID SLUG!"))
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_post_missing_content(client: AsyncClient) -> None:
    payload = make_post_data()
    del payload["content"]
    resp = await client.post("/posts/", json=payload)
    assert resp.status_code == 422


# --- PUT /posts/{post_id} (update) ---


@pytest.mark.asyncio
async def test_update_post(client: AsyncClient) -> None:
    create_resp = await client.post("/posts/", json=make_post_data())
    post = create_resp.json()

    resp = await client.put(f"/posts/{post['id']}", json={"title": "Updated Title"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated Title"
    assert data["slug"] == "test-post"  # unchanged


@pytest.mark.asyncio
async def test_update_post_multiple_fields(client: AsyncClient) -> None:
    create_resp = await client.post("/posts/", json=make_post_data())
    post = create_resp.json()

    resp = await client.put(
        f"/posts/{post['id']}",
        json={"title": "New Title", "slug": "new-slug", "excerpt": "Updated excerpt"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "New Title"
    assert data["slug"] == "new-slug"
    assert data["excerpt"] == "Updated excerpt"


@pytest.mark.asyncio
async def test_update_post_not_found(client: AsyncClient) -> None:
    resp = await client.put(f"/posts/{uuid.uuid4()}", json={"title": "Nope"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_post_slug_conflict(client: AsyncClient) -> None:
    await client.post("/posts/", json=make_post_data(slug="first"))
    create_resp = await client.post("/posts/", json=make_post_data(slug="second"))
    post = create_resp.json()

    resp = await client.put(f"/posts/{post['id']}", json={"slug": "first"})
    assert resp.status_code == 409


# --- DELETE /posts/{post_id} ---


@pytest.mark.asyncio
async def test_delete_post(client: AsyncClient) -> None:
    create_resp = await client.post("/posts/", json=make_post_data())
    post = create_resp.json()

    resp = await client.delete(f"/posts/{post['id']}")
    assert resp.status_code == 204

    # Verify it's gone
    resp = await client.get(f"/posts/{post['id']}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_post_not_found(client: AsyncClient) -> None:
    resp = await client.delete(f"/posts/{uuid.uuid4()}")
    assert resp.status_code == 404
