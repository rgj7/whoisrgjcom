"""add social links

Revision ID: d1b979b6d5ee
Revises: 9ed7bf3a6b74
Create Date: 2026-06-03 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d1b979b6d5ee"
down_revision: str | Sequence[str] | None = "9ed7bf3a6b74"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "social_link",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("platform", sa.String(length=50), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("length(trim(platform)) > 0", name="social_link_platform_not_empty"),
        sa.CheckConstraint("length(trim(url)) > 0", name="social_link_url_not_empty"),
        sa.PrimaryKeyConstraint("id", name=op.f("social_link_pkey")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("social_link")
