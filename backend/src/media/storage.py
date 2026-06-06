from functools import lru_cache
from urllib.parse import quote

from google.cloud import storage

from src.config import settings
from src.media.service import OUTPUT_CONTENT_TYPE

CACHE_CONTROL = "public, max-age=31536000, immutable"
PUBLIC_GCS_URL_TEMPLATE = "https://storage.googleapis.com/{bucket}/{object_name}"


@lru_cache(maxsize=1)
def get_storage_client() -> storage.Client:
    """Return a cached GCS client using Application Default Credentials."""
    return storage.Client()


def get_bucket_name() -> str:
    """Return the configured media bucket name."""
    if not settings.GCS_BUCKET_NAME:
        raise RuntimeError("GCS_BUCKET_NAME is not configured")
    return settings.GCS_BUCKET_NAME


def build_public_url(object_name: str, bucket_name: str | None = None) -> str:
    """Build the public URL for an object."""
    quoted_object_name = quote(object_name, safe="/")
    if settings.MEDIA_PUBLIC_BASE_URL:
        return f"{settings.MEDIA_PUBLIC_BASE_URL.rstrip('/')}/{quoted_object_name}"

    bucket = bucket_name or get_bucket_name()
    return PUBLIC_GCS_URL_TEMPLATE.format(
        bucket=bucket,
        object_name=quoted_object_name,
    )


def upload_image_object(
    object_name: str,
    data: bytes,
    content_type: str = OUTPUT_CONTENT_TYPE,
) -> str:
    """Upload optimized image bytes to GCS and return the public URL."""
    bucket_name = get_bucket_name()
    bucket = get_storage_client().bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.cache_control = CACHE_CONTROL
    blob.upload_from_string(data, content_type=content_type)
    return build_public_url(object_name, bucket_name=bucket_name)


def delete_object(object_name: str) -> None:
    """Delete an object from the configured media bucket."""
    bucket = get_storage_client().bucket(get_bucket_name())
    bucket.blob(object_name).delete()
