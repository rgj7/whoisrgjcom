import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.database import get_db
from src.posts.models import Post
from src.posts.schemas import PostCreate, PostResponse, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/", response_model=list[PostResponse], summary="List all posts")
async def list_posts(db: DbSession):
    result = await db.execute(select(Post).order_by(Post.created_at.desc()))
    return result.scalars().all()


@router.get("/{post_id}", response_model=PostResponse, summary="Get a post by ID")
async def get_post(post_id: uuid.UUID, db: DbSession):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new post",
)
async def create_post(data: PostCreate, db: DbSession):
    post = Post(**data.model_dump())
    db.add(post)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Slug '{data.slug}' already exists",
        )
    await db.refresh(post)
    return post


@router.put("/{post_id}", response_model=PostResponse, summary="Update a post")
async def update_post(post_id: uuid.UUID, data: PostUpdate, db: DbSession):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Slug '{data.slug}' already exists",
        )
    await db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a post")
async def delete_post(post_id: uuid.UUID, db: DbSession):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    await db.delete(post)
    await db.commit()
