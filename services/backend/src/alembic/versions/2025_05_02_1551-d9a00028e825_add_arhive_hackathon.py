"""add archive hackathon

Revision ID: d9a00028e825
Revises: e91189f7f83f
Create Date: 2025-05-02 15:51:29.010313

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d9a00028e825"
down_revision: Union[str, None] = "e91189f7f83f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "hackathons",
        sa.Column("is_archived", sa.Boolean(), server_default="false", nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("hackathons", "is_archived")