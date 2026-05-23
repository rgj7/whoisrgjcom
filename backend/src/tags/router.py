from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.tags.models import Tag
from src.tags.schemas import TagResponse

router = APIRouter(prefix="/admin/tags", tags=["tags"], redirect_slashes=False)


DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "/",
    response_model=list[TagResponse],
    summary="Search existing tags",
    description="Returns tags whose names start with the given prefix (case-insensitive). "
    "Returns all tags when no search query is provided.",
)
async def search_tags(
    search: str = Query(default="", min_length=0),
    db: DbSession = None,  # type: ignore[assignment]
):
    if not search:
        result = await db.execute(select(Tag).order_by(Tag.name))
        return [TagResponse.model_validate(tag) for tag in result.scalars().all()]

    pattern = f"{search.lower()}%"
    result = await db.execute(select(Tag).where(Tag.name.ilike(pattern)).order_by(Tag.name))
    return [TagResponse.model_validate(tag) for tag in result.scalars().all()]
