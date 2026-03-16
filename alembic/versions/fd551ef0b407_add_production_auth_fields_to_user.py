"""add production auth fields to user

Revision ID: fd551ef0b407
Revises: 4cfc92bae12b
Create Date: 2026-03-15 18:05:45.331022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fd551ef0b407"
down_revision: Union[str, Sequence[str], None] = "4cfc92bae12b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "user",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "user",
        sa.Column(
            "failed_login_attempts",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "user",
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "user",
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.alter_column("user", "is_active", server_default=None)
    op.alter_column("user", "is_verified", server_default=None)
    op.alter_column("user", "failed_login_attempts", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("user", "last_login_at")
    op.drop_column("user", "locked_until")
    op.drop_column("user", "failed_login_attempts")
    op.drop_column("user", "is_verified")
    op.drop_column("user", "is_active")