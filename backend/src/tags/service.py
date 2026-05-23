"""Tag resolution helpers for post create/update operations."""

import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.tags.models import Tag, post_tags


async def resolve_tags(tag_names: list[str], db: AsyncSession) -> list[Tag]:
    """Create or look up tags by name (case-insensitive) and return the Tag ORM objects.

    - All names are lowercased and stripped before processing.
    - Existing tags are matched case-insensitively.
    - New tags are inserted in a single batch.
    - Returns all resolved tags (both existing and newly created).
    """
    names = list({name.strip().lower() for name in tag_names if name.strip()})

    if not names:
        return []

    result = await db.execute(select(Tag).where(Tag.name.in_(names)))
    existing = {tag.name: tag for tag in result.scalars().all()}

    new_tags: list[Tag] = [Tag(name=name) for name in names if name not in existing]

    if new_tags:
        db.add_all(new_tags)
        await db.flush()

    return list(existing.values()) + new_tags


async def _delete_orphaned_tags(db: AsyncSession) -> None:
    """Delete tags that are no longer referenced by any post."""
    await db.execute(
        delete(Tag).where(
            Tag.id.not_in(
                select(post_tags.c.tag_id)
            )
        )
    )
    await db.flush()


async def set_post_tags(db: AsyncSession, post_id: uuid.UUID, tag_ids: list[uuid.UUID]) -> None:
    """Replace all tag associations for a post.

    Clears existing associations, inserts new ones, and deletes any tags
    that are no longer referenced by any post.
    """
    await db.execute(post_tags.delete().where(post_tags.c.post_id == post_id))

    if tag_ids:
        associations = [
            {"post_id": post_id, "tag_id": tag_id}
            for tag_id in tag_ids
        ]
        await db.execute(post_tags.insert(), associations)

    await _delete_orphaned_tags(db)
