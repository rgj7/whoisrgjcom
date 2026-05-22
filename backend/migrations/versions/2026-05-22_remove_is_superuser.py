"""remove is_superuser column from user table

Revision ID: b1c2d3e4f5a6
Revises: a1b2c3d4e5f6
Create Date: 2026-05-22
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b1c2d3e4f5a6"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("user", "is_superuser")


def downgrade() -> None:
    op.add_column(
        "user",
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"),
    )
