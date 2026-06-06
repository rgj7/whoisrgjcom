from io import BytesIO
from uuid import UUID

import httpx
import pytest
import pytest_asyncio
from PIL import Image
from sqlalchemy import select, text

from src.auth.service import hash_password
from src.config import settings
from src.media.models import Media
from src.media.storage import build_public_url

TEST_USER = {
    "username": "mediauser",
    "email": "media@example.com",
    "password": "password123",
}


async def _create_test_user(engine, user_id: str, username: str, email: str, password: str) -> None:
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
async def auth_headers(client: httpx.AsyncClient, test_engine) -> dict[str, str]:
    await _create_test_user(
        test_engine,
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        TEST_USER["username"],
        TEST_USER["email"],
        TEST_USER["password"],
    )

    login_resp = await client.post(
        "/auth/login",
        json={"username": TEST_USER["username"], "password": TEST_USER["password"]},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_gcs(monkeypatch):
    uploaded: list[dict] = []
    deleted: list[str] = []

    def fake_upload_image_object(object_name: str, data: bytes, content_type: str) -> str:
        uploaded.append({"object_name": object_name, "data": data, "content_type": content_type})
        return f"https://storage.googleapis.com/test-bucket/{object_name}"

    def fake_delete_object(object_name: str) -> None:
        deleted.append(object_name)

    monkeypatch.setattr("src.media.admin_router.upload_image_object", fake_upload_image_object)
    monkeypatch.setattr("src.media.admin_router.delete_object", fake_delete_object)
    return {"uploaded": uploaded, "deleted": deleted}


def make_image_bytes(image_format: str, size: tuple[int, int] = (80, 40)) -> bytes:
    output = BytesIO()
    Image.new("RGB", size, "blue").save(output, format=image_format)
    return output.getvalue()


def test_build_public_url_defaults_to_raw_gcs_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "MEDIA_PUBLIC_BASE_URL", "")

    url = build_public_url("media/posts/2026/06/test image.webp", bucket_name="test-bucket")

    assert url == "https://storage.googleapis.com/test-bucket/media/posts/2026/06/test%20image.webp"


def test_build_public_url_uses_media_public_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "MEDIA_PUBLIC_BASE_URL", "https://media.whoisrgj.com")

    url = build_public_url("media/posts/2026/06/test.webp", bucket_name="test-bucket")

    assert url == "https://media.whoisrgj.com/media/posts/2026/06/test.webp"


def test_build_public_url_quotes_object_name_in_cdn_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "MEDIA_PUBLIC_BASE_URL", "https://media.whoisrgj.com/")

    url = build_public_url("media/posts/2026/06/test image #1.webp", bucket_name="test-bucket")

    assert url == "https://media.whoisrgj.com/media/posts/2026/06/test%20image%20%231.webp"


@pytest.mark.asyncio
async def test_upload_image_requires_auth(client: httpx.AsyncClient) -> None:
    image_bytes = make_image_bytes("JPEG")

    resp = await client.post(
        "/admin/media/images",
        files={"file": ("test.jpg", image_bytes, "image/jpeg")},
    )

    assert resp.status_code in {401, 403}


@pytest.mark.asyncio
async def test_upload_rejects_non_image(client: httpx.AsyncClient, auth_headers: dict[str, str]) -> None:
    resp = await client.post(
        "/admin/media/images",
        headers=auth_headers,
        files={"file": ("not-image.txt", b"not an image", "text/plain")},
    )

    assert resp.status_code == 415


@pytest.mark.asyncio
async def test_upload_rejects_unsupported_image_type(client: httpx.AsyncClient, auth_headers: dict[str, str]) -> None:
    image_bytes = make_image_bytes("GIF")

    resp = await client.post(
        "/admin/media/images",
        headers=auth_headers,
        files={"file": ("test.gif", image_bytes, "image/gif")},
    )

    assert resp.status_code == 415


@pytest.mark.asyncio
async def test_upload_rejects_oversized_file(client: httpx.AsyncClient, auth_headers: dict[str, str]) -> None:
    oversized = b"x" * (5 * 1024 * 1024 + 1)

    resp = await client.post(
        "/admin/media/images",
        headers=auth_headers,
        files={"file": ("too-large.jpg", oversized, "image/jpeg")},
    )

    assert resp.status_code == 413


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("image_format", "filename", "mime_type"),
    [
        ("JPEG", "test.jpg", "image/jpeg"),
        ("PNG", "test.png", "image/png"),
        ("WEBP", "test.webp", "image/webp"),
    ],
)
async def test_upload_valid_image_returns_media_object_and_creates_row(
    client: httpx.AsyncClient,
    test_engine,
    auth_headers: dict[str, str],
    mock_gcs,
    image_format: str,
    filename: str,
    mime_type: str,
) -> None:
    image_bytes = make_image_bytes(image_format, size=(2000, 1000))

    resp = await client.post(
        "/admin/media/images",
        headers=auth_headers,
        files={"file": (filename, image_bytes, mime_type)},
    )

    assert resp.status_code == 201
    data = resp.json()
    assert UUID(data["id"])
    assert data["url"].startswith("https://storage.googleapis.com/test-bucket/media/posts/")
    assert data["object_name"].startswith("media/posts/")
    assert data["object_name"].endswith(".webp")
    assert data["content_type"] == "image/webp"
    assert data["size_bytes"] > 0
    assert data["width"] == 1600
    assert data["height"] == 800
    assert "created_at" in data

    assert len(mock_gcs["uploaded"]) == 1
    assert mock_gcs["uploaded"][0]["content_type"] == "image/webp"
    assert mock_gcs["uploaded"][0]["data"].startswith(b"RIFF")

    async with test_engine.connect() as conn:
        result = await conn.execute(select(Media).where(Media.id == UUID(data["id"])))
        media = result.mappings().one()
    assert media["object_name"] == data["object_name"]
    assert media["content_type"] == "image/webp"


@pytest.mark.asyncio
async def test_delete_media_removes_row_and_calls_object_delete(
    client: httpx.AsyncClient,
    test_engine,
    auth_headers: dict[str, str],
    mock_gcs,
) -> None:
    image_bytes = make_image_bytes("PNG")
    upload_resp = await client.post(
        "/admin/media/images",
        headers=auth_headers,
        files={"file": ("test.png", image_bytes, "image/png")},
    )
    assert upload_resp.status_code == 201
    media = upload_resp.json()

    delete_resp = await client.delete(f"/admin/media/{media['id']}", headers=auth_headers)

    assert delete_resp.status_code == 204
    assert mock_gcs["deleted"] == [media["object_name"]]

    async with test_engine.connect() as conn:
        result = await conn.execute(select(Media).where(Media.id == UUID(media["id"])))
        assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_media_not_found(client: httpx.AsyncClient, auth_headers: dict[str, str], mock_gcs) -> None:
    resp = await client.delete("/admin/media/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", headers=auth_headers)

    assert resp.status_code == 404
    assert mock_gcs["deleted"] == []
