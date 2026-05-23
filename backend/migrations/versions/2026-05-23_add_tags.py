"""add_tags

Revision ID: 784f44dd63e7
Revises: b1c2d3e4f5a6
Create Date: 2026-05-23 15:05:22.916910

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '784f44dd63e7'
down_revision: str | Sequence[str] | None = 'b1c2d3e4f5a6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tag",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "post_tags",
        sa.Column("post_id", sa.UUID(), nullable=False),
        sa.Column("tag_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["post.id"]),
        sa.ForeignKeyConstraint(["tag_id"], ["tag.id"]),
        sa.PrimaryKeyConstraint("post_id", "tag_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("post_tags")
    op.drop_table("tag")
