import uuid
from math import ceil
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import OptionalCurrentUser
from src.database import get_db
from src.posts.exceptions import PostNotFound
from src.posts.models import Post
from src.posts.schemas import PaginatedPosts, PostResponse

router = APIRouter(prefix="/posts", tags=["posts"])


DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "/",
    response_model=PaginatedPosts,
    summary="List published posts (paginated)",
    description="Returns a paginated list of published posts ordered by creation date (newest first).",
)
async def list_posts(
    db: DbSession,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
):
    # Get total count of published posts
    count_result = await db.execute(select(func.count(Post.id)).where(Post.published))
    total = count_result.scalar() or 0
    pages = ceil(total / limit) if total > 0 else 0

    # Get paginated published items
    offset = (page - 1) * limit
    result = await db.execute(
        select(Post).where(Post.published).order_by(Post.created_at.desc()).offset(offset).limit(limit)
    )
    items = [PostResponse.model_validate(post) for post in result.scalars().all()]

    return PaginatedPosts(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get(
    "/slug/{slug}",
    response_model=PostResponse,
    summary="Get a post by slug",
    description="Returns a single post by its slug. Unpublished posts require authentication.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Post not found"},
    },
)
async def get_post_by_slug(slug: str, db: DbSession, user: OptionalCurrentUser):
    result = await db.execute(select(Post).where(Post.slug == slug))
    post = result.scalar_one_or_none()
    if not post or (not post.published and user is None):
        raise PostNotFound(slug)
    return post


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Get a published post by ID",
    description="Returns a single published post by its UUID.",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Post not found"},
    },
)
async def get_post(post_id: uuid.UUID, db: DbSession):
    post = await db.get(Post, post_id)
    if not post or not post.published:
        raise PostNotFound(str(post_id))
    return post
