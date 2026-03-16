"""rename refresh token to token_hash

Revision ID: 34b644d3e491
Revises: eec1aaa6c068
Create Date: 2026-03-15 21:36:10.887104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34b644d3e491'
down_revision: Union[str, Sequence[str], None] = 'eec1aaa6c068'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
