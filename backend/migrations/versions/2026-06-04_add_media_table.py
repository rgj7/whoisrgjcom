"""add media table

Revision ID: 2f4d7e8a9b10
Revises: d1b979b6d5ee
Create Date: 2026-06-04 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2f4d7e8a9b10"
down_revision: str | Sequence[str] | None = "d1b979b6d5ee"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "media",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("object_name", sa.String(length=500), nullable=False),
        sa.Column("public_url", sa.String(length=1000), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["user.id"], name=op.f("media_created_by_fkey")),
        sa.PrimaryKeyConstraint("id", name=op.f("media_pkey")),
        sa.UniqueConstraint("object_name", name=op.f("media_object_name_key")),
    )
    op.create_index("media_created_at_idx", "media", ["created_at"], unique=False)
    op.create_index("media_created_by_idx", "media", ["created_by"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("media_created_by_idx", table_name="media")
    op.drop_index("media_created_at_idx", table_name="media")
    op.drop_table("media")
