"""Business logic for travels batch operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.travels.models import Travel


async def resolve_travels(db: AsyncSession) -> dict[str, list[str]]:
    """Return {visited: [...], bucketlist: [...]} sorted country codes."""
    result = await db.execute(select(Travel).order_by(Travel.country_code))
    travels = result.scalars().all()

    by_status: dict[str, list[str]] = {"visited": [], "bucketlist": []}
    for travel in travels:
        by_status.setdefault(travel.status, []).append(travel.country_code)

    for key in by_status:
        by_status[key].sort()

    return by_status


async def batch_replace_travels(
    db: AsyncSession,
    visited: list[str],
    bucketlist: list[str],
) -> None:
    """Atomically replace the entire travels state.

    - Normalises codes to upper-case.
    - Deduplicates within each list.
    - Inserts new records, updates status on existing, deletes stale ones.
    """

    visited_set = {code.upper().strip() for code in visited if code.strip()}
    bucketlist_set = {code.upper().strip() for code in bucketlist if code.strip()}
    all_codes = visited_set | bucketlist_set

    # Fetch ALL existing records so stale ones outside all_codes are caught
    result = await db.execute(select(Travel))
    existing = {t.country_code: t for t in result.scalars().all()}
    codes_to_delete = set(existing.keys())

    for code in visited_set:
        codes_to_delete.discard(code)
        if code in existing:
            if existing[code].status != "visited":
                existing[code].status = "visited"
        else:
            db.add(Travel(country_code=code, status="visited"))

    for code in bucketlist_set:
        codes_to_delete.discard(code)
        if code in existing:
            if existing[code].status != "bucketlist":
                existing[code].status = "bucketlist"
        else:
            db.add(Travel(country_code=code, status="bucketlist"))

    # Delete stale records
    for code in codes_to_delete:
        await db.delete(existing[code])

    await db.flush()
