"""add archive contest

Revision ID: 5f2b0234ff1e
Revises: d9a00028e825
Create Date: 2025-05-02 15:54:41.002530

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5f2b0234ff1e"
down_revision: Union[str, None] = "d9a00028e825"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "contests",
        sa.Column(
            "is_archived",
            sa.Boolean(),
            server_default="false",
            nullable=False
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("contests", "is_archived")