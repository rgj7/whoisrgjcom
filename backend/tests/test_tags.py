"""Tests for the tag feature: tag search, post creation with tags, post update with tags."""

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.auth.service import hash_password
from src.config import settings

# --- Auth helpers (same as test_posts.py) ---

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
        pass
    else:
        try:
            await eng.dispose()
        except RuntimeError:
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


def make_post_data(
    title: str = "Test Post",
    slug: str = "test-post",
    content: dict | None = None,
    excerpt: str | None = None,
    tags: list[str] | None = None,
    published: bool = True,
) -> dict:
    data: dict = {
        "title": title,
        "slug": slug,
        "content": content or {"body": "Hello world"},
        "published": published,
    }
    if excerpt is not None:
        data["excerpt"] = excerpt
    if tags is not None:
        data["tags"] = tags
    return data


# --- GET /admin/tags (search) ---


@pytest.mark.asyncio
async def test_search_tags_empty(client: httpx.AsyncClient) -> None:
    """Search with no results returns empty list."""
    resp = await client.get("/admin/tags/?search=nonexistent")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_search_tags_prefix_match(client: httpx.AsyncClient) -> None:
    """Search returns tags matching the prefix (case-insensitive)."""
    headers = await get_auth_header(client)
    # Create a post with tags to populate the tag table
    await client.post("/admin/posts/", json=make_post_data(tags=["Python", "Django"]), headers=headers)

    resp = await client.get("/admin/tags/?search=py")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "python"


@pytest.mark.asyncio
async def test_search_tags_case_insensitive(client: httpx.AsyncClient) -> None:
    """Search is case-insensitive."""
    headers = await get_auth_header(client)
    await client.post("/admin/posts/", json=make_post_data(tags=["Python"]), headers=headers)

    resp = await client.get("/admin/tags/?search=PY")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "python"


@pytest.mark.asyncio
async def test_search_tags_no_query(client: httpx.AsyncClient) -> None:
    """Empty search returns empty list."""
    resp = await client.get("/admin/tags/")
    assert resp.status_code == 200
    data = resp.json()
    assert data == []


# --- POST /admin/posts (create with tags) ---


@pytest.mark.asyncio
async def test_create_post_with_tags(client: httpx.AsyncClient) -> None:
    """Creating a post with tags creates them and associates them."""
    headers = await get_auth_header(client)
    resp = await client.post(
        "/admin/posts/",
        json=make_post_data(tags=["Python", "FastAPI"]),
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert set(data["tags"]) == {"fastapi", "python"}


@pytest.mark.asyncio
async def test_create_post_tags_case_normalized(client: httpx.AsyncClient) -> None:
    """Tags are lowercased on creation."""
    headers = await get_auth_header(client)
    resp = await client.post(
        "/admin/posts/",
        json=make_post_data(tags=["PyThOn", "FaStApI"]),
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert set(data["tags"]) == {"fastapi", "python"}


@pytest.mark.asyncio
async def test_create_post_tags_deduplication(client: httpx.AsyncClient) -> None:
    """Duplicate tag names are deduplicated."""
    headers = await get_auth_header(client)
    resp = await client.post(
        "/admin/posts/",
        json=make_post_data(tags=["Python", "python", "PYTHON"]),
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["tags"] == ["python"]


@pytest.mark.asyncio
async def test_create_post_no_tags(client: httpx.AsyncClient) -> None:
    """Creating a post without tags returns empty list."""
    headers = await get_auth_header(client)
    resp = await client.post(
        "/admin/posts/",
        json=make_post_data(tags=[]),
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["tags"] == []


@pytest.mark.asyncio
async def test_create_post_tags_sorted(client: httpx.AsyncClient) -> None:
    """Tags in response are sorted alphabetically."""
    headers = await get_auth_header(client)
    resp = await client.post(
        "/admin/posts/",
        json=make_post_data(tags=["zebra", "alpha", "beta"]),
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["tags"] == ["alpha", "beta", "zebra"]


@pytest.mark.asyncio
async def test_create_post_tags_whitespace_trimming(client: httpx.AsyncClient) -> None:
    """Tag names are trimmed of whitespace."""
    headers = await get_auth_header(client)
    resp = await client.post(
        "/admin/posts/",
        json=make_post_data(tags=["  python  ", "  fastapi  "]),
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert set(data["tags"]) == {"fastapi", "python"}


# --- PUT /admin/posts/{id} (update tags) ---


@pytest.mark.asyncio
async def test_update_post_tags(client: httpx.AsyncClient) -> None:
    """Updating a post replaces its tags entirely."""
    headers = await get_auth_header(client)
    create_resp = await client.post(
        "/admin/posts/",
        json=make_post_data(slug="first-post", tags=["Python"]),
        headers=headers,
    )
    post_id = create_resp.json()["id"]

    resp = await client.put(
        f"/admin/posts/{post_id}",
        json={"tags": ["Django", "REST"]},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert set(data["tags"]) == {"django", "rest"}


@pytest.mark.asyncio
async def test_update_post_remove_all_tags(client: httpx.AsyncClient) -> None:
    """Setting empty tags removes all tag associations."""
    headers = await get_auth_header(client)
    create_resp = await client.post(
        "/admin/posts/",
        json=make_post_data(slug="tagged-post", tags=["Python"]),
        headers=headers,
    )
    post_id = create_resp.json()["id"]

    resp = await client.put(
        f"/admin/posts/{post_id}",
        json={"tags": []},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["tags"] == []


@pytest.mark.asyncio
async def test_update_post_other_fields_unchanged(client: httpx.AsyncClient) -> None:
    """Updating tags doesn't affect other fields."""
    headers = await get_auth_header(client)
    create_resp = await client.post(
        "/admin/posts/",
        json=make_post_data(slug="unchanged", title="Original Title", excerpt="Original excerpt"),
        headers=headers,
    )
    post_id = create_resp.json()["id"]

    resp = await client.put(
        f"/admin/posts/{post_id}",
        json={"tags": ["NewTag"]},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Original Title"
    assert data["excerpt"] == "Original excerpt"
    assert set(data["tags"]) == {"newtag"}


@pytest.mark.asyncio
async def test_update_post_partial_fields_with_tags(client: httpx.AsyncClient) -> None:
    """Partial update with tags only changes specified fields."""
    headers = await get_auth_header(client)
    create_resp = await client.post(
        "/admin/posts/",
        json=make_post_data(slug="partial", title="Before", tags=["Python"]),
        headers=headers,
    )
    post_id = create_resp.json()["id"]

    resp = await client.put(
        f"/admin/posts/{post_id}",
        json={"title": "After", "tags": ["NewTag"]},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "After"
    assert data["slug"] == "partial"  # unchanged
    assert set(data["tags"]) == {"newtag"}


# --- Tag resolution: existing tags reused ---


@pytest.mark.asyncio
async def test_tag_resolution_reuses_existing_tags(client: httpx.AsyncClient) -> None:
    """Creating a second post with an existing tag reuses the same tag."""
    headers = await get_auth_header(client)
    # First post creates "python" tag
    await client.post("/admin/posts/", json=make_post_data(slug="post-one", tags=["Python"]), headers=headers)
    # Second post with same tag name
    resp = await client.post(
        "/admin/posts/",
        json=make_post_data(slug="post-two", tags=["Python", "FastAPI"]),
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert set(data["tags"]) == {"fastapi", "python"}


# --- Unauthorized access ---


@pytest.mark.asyncio
async def test_create_post_tags_unauthorized(client: httpx.AsyncClient) -> None:
    """Creating a post with tags requires authentication."""
    resp = await client.post("/admin/posts/", json=make_post_data(tags=["Python"]))
    assert resp.status_code == 401


# --- Tag search: multiple results ---


@pytest.mark.asyncio
async def test_search_tags_multiple_results(client: httpx.AsyncClient) -> None:
    """Search returns all tags matching the prefix."""
    headers = await get_auth_header(client)
    await client.post("/admin/posts/", json=make_post_data(slug="p1", tags=["Python", "JavaScript", "Java"]), headers=headers)

    resp = await client.get("/admin/tags/?search=ja")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    names = {d["name"] for d in data}
    assert names == {"java", "javascript"}


@pytest.mark.asyncio
async def test_search_tags_returns_sorted(client: httpx.AsyncClient) -> None:
    """Search results are returned sorted by tag name."""
    headers = await get_auth_header(client)
    await client.post(
        "/admin/posts/",
        json=make_post_data(slug="p1", tags=["Zebra", "Alpha", "Beta"]),
        headers=headers,
    )

    resp = await client.get("/admin/tags/?search=")
    assert resp.status_code == 200
    # Empty search should return empty or all — test prefix match
    resp = await client.get("/admin/tags/?search=a")
    data = resp.json()
    assert len(data) >= 1
    # Check sorted
    names = [d["name"] for d in data]
    assert names == sorted(names)


# --- Tag resolution: mixed existing and new ---


@pytest.mark.asyncio
async def test_create_post_mixed_existing_and_new_tags(client: httpx.AsyncClient) -> None:
    """Creating a post with some existing and some new tags works correctly."""
    headers = await get_auth_header(client)
    # First post creates "python" tag
    await client.post("/admin/posts/", json=make_post_data(slug="first", tags=["Python"]), headers=headers)
    # Second post uses "python" (existing) and adds "Go"
    resp = await client.post(
        "/admin/posts/",
        json=make_post_data(slug="second", tags=["Python", "Go"]),
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert set(data["tags"]) == {"go", "python"}


@pytest.mark.asyncio
async def test_update_post_add_tags_to_empty(client: httpx.AsyncClient) -> None:
    """Adding tags to a post that had none."""
    headers = await get_auth_header(client)
    create_resp = await client.post(
        "/admin/posts/",
        json=make_post_data(slug="no-tags", tags=[]),
        headers=headers,
    )
    post_id = create_resp.json()["id"]

    resp = await client.put(
        f"/admin/posts/{post_id}",
        json={"tags": ["Rust", "WebAssembly"]},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert set(data["tags"]) == {"rust", "webassembly"}


@pytest.mark.asyncio
async def test_update_post_replace_tags(client: httpx.AsyncClient) -> None:
    """Replacing all tags with completely different ones."""
    headers = await get_auth_header(client)
    create_resp = await client.post(
        "/admin/posts/",
        json=make_post_data(slug="replace", tags=["Old1", "Old2"]),
        headers=headers,
    )
    post_id = create_resp.json()["id"]

    resp = await client.put(
        f"/admin/posts/{post_id}",
        json={"tags": ["New1", "New2", "New3"]},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert set(data["tags"]) == {"new1", "new2", "new3"}


# --- Tag name uniqueness ---


@pytest.mark.asyncio
async def test_tag_name_case_insensitive_uniqueness(client: httpx.AsyncClient) -> None:
    """Creating a post with 'Python' then 'python' should reuse the existing tag."""
    headers = await get_auth_header(client)
    # First post creates "python"
    await client.post("/admin/posts/", json=make_post_data(slug="p1", tags=["Python"]), headers=headers)
    # Second post with "python" (same lowercase) should reuse
    resp = await client.post(
        "/admin/posts/",
        json=make_post_data(slug="p2", tags=["python"]),
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["tags"] == ["python"]


# --- Public post endpoints with tags ---


@pytest.mark.asyncio
async def test_public_post_response_includes_tags(client: httpx.AsyncClient) -> None:
    """Public post endpoints return tags in the response."""
    headers = await get_auth_header(client)
    create_resp = await client.post(
        "/admin/posts/",
        json=make_post_data(slug="public-tagged", published=True, tags=["Public", "Tagged"]),
        headers=headers,
    )
    post_id = create_resp.json()["id"]

    # Public endpoint
    resp = await client.get(f"/posts/{post_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert set(data["tags"]) == {"public", "tagged"}


@pytest.mark.asyncio
async def test_public_posts_list_includes_tags(client: httpx.AsyncClient) -> None:
    """Public posts list returns tags for each post."""
    headers = await get_auth_header(client)
    await client.post(
        "/admin/posts/",
        json=make_post_data(slug="listed-post", published=True, tags=["Listed"]),
        headers=headers,
    )

    resp = await client.get("/posts/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    # Find our post
    our_post = next((p for p in data["items"] if p["slug"] == "listed-post"), None)
    assert our_post is not None
    assert set(our_post["tags"]) == {"listed"}


@pytest.mark.asyncio
async def test_public_post_by_slug_includes_tags(client: httpx.AsyncClient) -> None:
    """Public post by slug returns tags."""
    headers = await get_auth_header(client)
    await client.post(
        "/admin/posts/",
        json=make_post_data(slug="slug-test", published=True, tags=["SlugTest"]),
        headers=headers,
    )

    resp = await client.get("/posts/slug/slug-test")
    assert resp.status_code == 200
    data = resp.json()
    assert set(data["tags"]) == {"slugtest"}


@pytest.mark.asyncio
async def test_orphan_tag_cleanup_on_update(client: httpx.AsyncClient) -> None:
    """Removing the last tag from a post deletes the tag from the database."""
    headers = await get_auth_header(client)
    create_resp = await client.post(
        "/admin/posts/",
        json=make_post_data(slug="orphan-post", tags=["OrphanTag"]),
        headers=headers,
    )
    post_id = create_resp.json()["id"]

    # Verify tag exists in DB
    async with create_async_engine(url=settings.DATABASE_URL, pool_pre_ping=True).connect() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM tag WHERE name = 'orphantag'"))
        assert result.scalar() == 1

    # Remove the tag
    await client.put(
        f"/admin/posts/{post_id}",
        json={"tags": []},
        headers=headers,
    )

    # Verify tag is deleted from DB
    async with create_async_engine(url=settings.DATABASE_URL, pool_pre_ping=True).connect() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM tag WHERE name = 'orphantag'"))
        assert result.scalar() == 0


@pytest.mark.asyncio
async def test_shared_tag_not_deleted_on_cleanup(client: httpx.AsyncClient) -> None:
    """Tags still referenced by other posts are NOT deleted."""
    headers = await get_auth_header(client)
    # Two posts sharing "shared"
    await client.post(
        "/admin/posts/",
        json=make_post_data(slug="post-a", tags=["Shared", "OnlyA"]),
        headers=headers,
    )
    await client.post(
        "/admin/posts/",
        json=make_post_data(slug="post-b", tags=["Shared", "OnlyB"]),
        headers=headers,
    )

    # Remove "Shared" from post-a — it should survive because post-b still uses it
    create_resp = await client.get("/admin/posts/")
    post_a_id = next(p["id"] for p in create_resp.json()["items"] if p["slug"] == "post-a")
    await client.put(
        f"/admin/posts/{post_a_id}",
        json={"tags": ["OnlyA"]},
        headers=headers,
    )

    # Verify "shared" still exists
    async with create_async_engine(url=settings.DATABASE_URL, pool_pre_ping=True).connect() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM tag WHERE name = 'shared'"))
        assert result.scalar() == 1

    # Verify "onlya" still exists (still on post-a)
    async with create_async_engine(url=settings.DATABASE_URL, pool_pre_ping=True).connect() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM tag WHERE name = 'onlya'"))
        assert result.scalar() == 1

    # Verify "onlyb" still exists (still on post-b)
    async with create_async_engine(url=settings.DATABASE_URL, pool_pre_ping=True).connect() as conn:
        result = await conn.execute(text("SELECT COUNT(*) FROM tag WHERE name = 'onlyb'"))
        assert result.scalar() == 1
