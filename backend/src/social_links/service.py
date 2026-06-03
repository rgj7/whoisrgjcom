"""Business logic for social links."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.social_links.models import SocialLink
from src.social_links.schemas import SocialLinkCreate


async def resolve_social_links(db: AsyncSession) -> list[SocialLink]:
    """Return social links ordered for public display."""
    result = await db.execute(select(SocialLink).order_by(SocialLink.sort_order, SocialLink.created_at))
    return list(result.scalars().all())


async def batch_replace_social_links(db: AsyncSession, links: list[SocialLinkCreate]) -> None:
    """Replace the entire social links list with trimmed, ordered links."""
    result = await db.execute(select(SocialLink))
    existing = result.scalars().all()
    for link in existing:
        await db.delete(link)

    for index, link in enumerate(links):
        platform = link.platform.strip()
        url = str(link.url).strip()
        if not platform or not url:
            continue

        db.add(
            SocialLink(
                platform=platform,
                url=url,
                sort_order=index,
            ),
        )

    await db.flush()
