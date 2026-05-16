import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentUser
from src.database import get_db
from src.posts.exceptions import PostNotFound, PostSlugConflict
from src.posts.models import Post
from src.posts.schemas import PostCreate, PostResponse, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "/",
    response_model=list[PostResponse],
    summary="List all posts",
    description="Returns all posts ordered by creation date (newest first).",
    responses={
        status.HTTP_200_OK: {"model": list[PostResponse], "description": "Successful response"},
    },
)
async def list_posts(db: DbSession):
    result = await db.execute(select(Post).order_by(Post.created_at.desc()))
    return result.scalars().all()


@router.get(
    "/slug/{slug}",
    response_model=PostResponse,
    summary="Get a post by slug",
    description="Returns a single post by its slug.",
    responses={
        status.HTTP_200_OK: {"description": "Successful response"},
        status.HTTP_404_NOT_FOUND: {"description": "Post not found"},
    },
)
async def get_post_by_slug(slug: str, db: DbSession):
    result = await db.execute(select(Post).where(Post.slug == slug))
    post = result.scalar_one_or_none()
    if not post:
        raise PostNotFound(slug)
    return post


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Get a post by ID",
    description="Returns a single post by its UUID.",
    responses={
        status.HTTP_200_OK: {"description": "Successful response"},
        status.HTTP_404_NOT_FOUND: {"description": "Post not found"},
    },
)
async def get_post(post_id: uuid.UUID, db: DbSession):
    post = await db.get(Post, post_id)
    if not post:
        raise PostNotFound(str(post_id))
    return post


@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new post",
    description="Creates a new post. Fails with 409 if the slug is already taken.",
    responses={
        status.HTTP_201_CREATED: {"description": "Post created successfully"},
        status.HTTP_409_CONFLICT: {"description": "Slug already exists"},
    },
)
async def create_post(data: PostCreate, user: CurrentUser, db: DbSession):
    post = Post(**data.model_dump())
    db.add(post)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise PostSlugConflict(data.slug)
    await db.refresh(post)
    return post


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    summary="Update a post",
    description="Partially updates a post. Only provided fields are changed.",
    responses={
        status.HTTP_200_OK: {"description": "Post updated successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Post not found"},
        status.HTTP_409_CONFLICT: {"description": "Slug already exists"},
    },
)
async def update_post(post_id: uuid.UUID, data: PostUpdate, user: CurrentUser, db: DbSession):
    post = await db.get(Post, post_id)
    if not post:
        raise PostNotFound(str(post_id))

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise PostSlugConflict(data.slug)
    await db.refresh(post)
    return post


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a post",
    description="Permanently deletes a post by its UUID.",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Post deleted successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Post not found"},
    },
)
async def delete_post(post_id: uuid.UUID, user: CurrentUser, db: DbSession):
    post = await db.get(Post, post_id)
    if not post:
        raise PostNotFound(str(post_id))
    await db.delete(post)
    await db.commit()
