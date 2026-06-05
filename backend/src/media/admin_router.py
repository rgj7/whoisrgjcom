import uuid
from asyncio import to_thread
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentUser
from src.database import get_db
from src.media.exceptions import MediaNotFound
from src.media.models import Media
from src.media.schemas import MediaResponse
from src.media.service import optimize_image, read_upload_bytes
from src.media.storage import delete_object, upload_image_object

router = APIRouter(prefix="/admin/media", tags=["admin"])

DbSession = Annotated[AsyncSession, Depends(get_db)]
ImageUpload = Annotated[UploadFile, File(...)]


def build_post_image_object_name(media_id: uuid.UUID | None = None) -> str:
    """Build the canonical object name for an uploaded post image."""
    now = datetime.now(UTC)
    object_id = media_id or uuid.uuid4()
    return f"media/posts/{now:%Y/%m}/{object_id}.webp"


@router.post(
    "/images",
    response_model=MediaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a post image",
    description="Validates, optimizes, uploads, and tracks an admin post image. Admin only.",
    responses={
        status.HTTP_201_CREATED: {"description": "Image uploaded successfully"},
        status.HTTP_413_CONTENT_TOO_LARGE: {"description": "Uploaded file is too large"},
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {"description": "Unsupported or invalid image type"},
    },
)
async def upload_post_image(file: ImageUpload, user: CurrentUser, db: DbSession):
    input_bytes = await read_upload_bytes(file)
    optimized = await to_thread(optimize_image, input_bytes)

    object_name = build_post_image_object_name()
    public_url = await to_thread(
        upload_image_object,
        object_name,
        optimized.data,
        optimized.content_type,
    )

    media = Media(
        object_name=object_name,
        public_url=public_url,
        content_type=optimized.content_type,
        size_bytes=optimized.size_bytes,
        width=optimized.width,
        height=optimized.height,
        created_by=user.id,
    )
    db.add(media)

    try:
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        await _delete_object_best_effort(object_name)
        raise

    await db.refresh(media)
    return media


@router.delete(
    "/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete media",
    description="Deletes a media row and best-effort deletes the matching GCS object. Admin only.",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Media deleted successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Media not found"},
    },
)
async def delete_media(media_id: uuid.UUID, user: CurrentUser, db: DbSession):
    media = await db.get(Media, media_id)
    if not media:
        raise MediaNotFound(str(media_id))

    await _delete_object_best_effort(media.object_name)
    await db.delete(media)
    await db.commit()


async def _delete_object_best_effort(object_name: str) -> None:
    try:
        await to_thread(delete_object, object_name)
    except Exception:
        pass
