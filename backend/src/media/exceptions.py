from fastapi import HTTPException, status


class MediaNotFound(HTTPException):
    def __init__(self, media_id: str | None = None):
        detail = "Media not found"
        if media_id:
            detail = f"Media '{media_id}' not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class MediaUploadTooLarge(HTTPException):
    def __init__(self, max_bytes: int):
        super().__init__(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Uploaded file exceeds maximum size of {max_bytes} bytes",
        )


class UnsupportedMediaType(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported or invalid image type. Accepted formats are JPEG, PNG, and WebP.",
        )
