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
    op.alter_column(
        "post",
        "content",
        existing_type=sa.Text(),
        type_=JSONB(),
        postgresql_using="content::jsonb",
    )


def downgrade() -> None:
    """Convert JSONB back to Text."""
    op.alter_column(
        "post",
        "content",
        existing_type=JSONB(),
        type_=sa.Text(),
        postgresql_using="content::text",
    )
