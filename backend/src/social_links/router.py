from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentUser
from src.database import get_db
from src.social_links.schemas import SocialLinksBatchCreate, SocialLinksResponse
from src.social_links.service import batch_replace_social_links, resolve_social_links

router = APIRouter(prefix="/social-links", tags=["social-links"])
admin_router = APIRouter(prefix="/admin/social-links", tags=["admin"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "/",
    response_model=SocialLinksResponse,
    summary="Get social links",
    description="Returns social media links ordered for public display.",
)
async def get_social_links(db: DbSession):
    return SocialLinksResponse(links=await resolve_social_links(db))


@admin_router.post(
    "/",
    response_model=SocialLinksResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Batch replace social links",
    description="Atomically replaces all social links with the provided ordered list.",
)
async def batch_create_social_links(
    data: SocialLinksBatchCreate,
    user: CurrentUser,
    db: DbSession,
):
    await batch_replace_social_links(db, data.links)
    await db.commit()
    return SocialLinksResponse(links=await resolve_social_links(db))
