from dataclasses import dataclass
from io import BytesIO

from fastapi import UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

from src.config import settings
from src.media.exceptions import MediaUploadTooLarge, UnsupportedMediaType

ACCEPTED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}
OUTPUT_CONTENT_TYPE = "image/webp"
WEBP_QUALITY = 85
WEBP_METHOD = 6
READ_CHUNK_SIZE_BYTES = 64 * 1024


@dataclass(frozen=True)
class OptimizedImage:
    data: bytes
    content_type: str
    size_bytes: int
    width: int
    height: int


async def read_upload_bytes(file: UploadFile, max_bytes: int | None = None) -> bytes:
    """Read an uploaded file into memory while enforcing a maximum byte size."""
    max_size = max_bytes if max_bytes is not None else settings.MEDIA_MAX_UPLOAD_BYTES
    chunks: list[bytes] = []
    total_size = 0

    while chunk := await file.read(READ_CHUNK_SIZE_BYTES):
        total_size += len(chunk)
        if total_size > max_size:
            raise MediaUploadTooLarge(max_size)
        chunks.append(chunk)

    return b"".join(chunks)


def optimize_image(input_bytes: bytes, max_width: int | None = None) -> OptimizedImage:
    """Validate image bytes and return an optimized, metadata-stripped WebP image."""
    target_max_width = max_width if max_width is not None else settings.MEDIA_MAX_WIDTH
    image = _open_verified_image(input_bytes)

    image = ImageOps.exif_transpose(image)
    image = _normalize_image_mode(image)
    image.thumbnail((target_max_width, image.height), Image.Resampling.LANCZOS)
    image = _strip_metadata(image)

    output = BytesIO()
    image.save(output, format="WEBP", quality=WEBP_QUALITY, method=WEBP_METHOD, optimize=True)
    output_bytes = output.getvalue()
    width, height = image.size

    return OptimizedImage(
        data=output_bytes,
        content_type=OUTPUT_CONTENT_TYPE,
        size_bytes=len(output_bytes),
        width=width,
        height=height,
    )


def _open_verified_image(input_bytes: bytes) -> Image.Image:
    try:
        with Image.open(BytesIO(input_bytes)) as image:
            image_format = image.format
            image.verify()

        if image_format not in ACCEPTED_IMAGE_FORMATS:
            raise UnsupportedMediaType()

        with Image.open(BytesIO(input_bytes)) as image:
            image.load()
            return image.copy()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise UnsupportedMediaType() from None


def _normalize_image_mode(image: Image.Image) -> Image.Image:
    if image.mode in {"RGB", "RGBA"}:
        return image
    if image.mode == "P" and "transparency" in image.info:
        return image.convert("RGBA")
    return image.convert("RGB")


def _strip_metadata(image: Image.Image) -> Image.Image:
    clean_image = Image.new(image.mode, image.size)
    clean_image.paste(image)
    return clean_image
