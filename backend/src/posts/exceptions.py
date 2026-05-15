from fastapi import HTTPException, status


class PostNotFound(HTTPException):
    def __init__(self, post_id: str | None = None):
        detail = "Post not found"
        if post_id:
            detail = f"Post '{post_id}' not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class PostSlugConflict(HTTPException):
    def __init__(self, slug: str | None = None):
        detail = "A post with this slug already exists"
        if slug is not None:
            detail = f"Slug '{slug}' already exists"
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )
