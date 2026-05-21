"""add post category column

Revision ID: 20260520_category
Revises: 20260519_profile
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260520_category"
down_revision: Union[str, None] = "20260519_profile"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("category", sa.String(length=32), server_default="life", nullable=False))


def downgrade() -> None:
    op.drop_column("posts", "category")
