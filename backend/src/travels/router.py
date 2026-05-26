from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import CurrentUser
from src.database import get_db
from src.travels.exceptions import TravelNotFound
from src.travels.models import Travel
from src.travels.schemas import TravelsBatchCreate, TravelsResponse
from src.travels.service import batch_replace_travels, resolve_travels

router = APIRouter(prefix="/travels", tags=["travels"])
admin_router = APIRouter(prefix="/admin/travels", tags=["admin"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


# ── Public endpoints ──────────────────────────────────────────────


@router.get(
    "/",
    response_model=TravelsResponse,
    summary="Get all travels",
    description="Returns visited and bucketlist country codes.",
)
async def get_travels(db: DbSession):
    return TravelsResponse(**await resolve_travels(db))


# ── Admin endpoints ───────────────────────────────────────────────


@admin_router.post(
    "/",
    response_model=TravelsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Batch replace travels",
    description="Atomically replaces all travels with the provided visited and bucketlist lists.",
)
async def batch_create_travels(
    data: TravelsBatchCreate,
    user: CurrentUser,
    db: DbSession,
):
    await batch_replace_travels(db, data.visited, data.bucketlist)
    await db.commit()
    return TravelsResponse(**await resolve_travels(db))


@admin_router.delete(
    "/{country_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a travel",
    description="Removes a single country from the travels list.",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Travel deleted successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Travel not found"},
    },
)
async def delete_travel(
    country_code: str,
    user: CurrentUser,
    db: DbSession,
):
    code = country_code.upper().strip()
    result = await db.execute(select(Travel).where(Travel.country_code == code))
    travel = result.scalars().first()
    if not travel:
        raise TravelNotFound(code)
    await db.delete(travel)
    await db.commit()
