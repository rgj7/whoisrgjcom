"""Tag resolution helpers for post create/update operations."""

from sqlalchemy import select
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

    # Look up existing tags
    result = await db.execute(select(Tag).where(Tag.name.in_(names)))
    existing = {tag.name: tag for tag in result.scalars().all()}

    # Create new tags
    new_tags: list[Tag] = []
    for name in names:
        if name not in existing:
            tag = Tag(name=name)
            new_tags.append(tag)

    if new_tags:
        db.add_all(new_tags)
        await db.flush()

    # Re-fetch to ensure all tags (including newly created) are loaded
    all_ids = [tag.id for tag in existing.values()] + [tag.id for tag in new_tags]
    result = await db.execute(select(Tag).where(Tag.id.in_(all_ids)))
    return list(result.scalars().all())


async def set_post_tags(db: AsyncSession, post_id, tag_ids: list):
    """Replace all tag associations for a post.

    Clears existing associations and inserts new ones in a single batch.
    """
    if not tag_ids:
        await db.execute(post_tags.delete().where(post_tags.c.post_id == post_id))
        return

    # Delete existing associations
    await db.execute(post_tags.delete().where(post_tags.c.post_id == post_id))

    # Insert new associations
    associations = [
        {"post_id": post_id, "tag_id": tag_id}
        for tag_id in tag_ids
    ]
    await db.execute(post_tags.insert(), associations)
