"""convert post content from text to jsonb

Revision ID: a1b2c3d4e5f6
Revises: 032d97aaffb8
Create Date: 2026-05-21 15:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "032d97aaffb8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Convert content column from Text to JSONB."""
    # Step 1: Add a temporary text column
    op.add_column("post", sa.Column("content_old", sa.Text(), nullable=True))

    # Step 2: Copy data from text to the new JSONB column
    # We'll use a raw SQL statement since Alembic doesn't know about JSONB yet
    op.execute("ALTER TABLE post ADD COLUMN content_new JSONB")
    op.execute("UPDATE post SET content_new = content_old::jsonb")

    # Step 3: Drop old column and rename new one
    op.drop_column("post", "content_old")
    op.alter_column("post", "content_new", new_column_name="content")


def downgrade() -> None:
    """Convert JSONB back to Text."""
    op.add_column("post", sa.Column("content_old", JSONB(), nullable=True))
    op.execute("ALTER TABLE post ADD COLUMN content_new TEXT")
    op.execute("UPDATE post SET content_new = content_old::text")
    op.drop_column("post", "content_old")
    op.alter_column("post", "content_new", new_column_name="content")
