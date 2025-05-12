"""add archive contest and hackathon tasks

Revision ID: 110efdfc7069
Revises: 5f2b0234ff1e
Create Date: 2025-05-02 16:03:30.254951

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "110efdfc7069"
down_revision: Union[str, None] = "5f2b0234ff1e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "contest_tasks",
        sa.Column(
            "is_archived",
            sa.Boolean(),
            server_default="false",
            nullable=False
        )
    )
    op.add_column(
        "hackathon_tasks",
        sa.Column(
            "is_archived",
            sa.Boolean(),
            server_default="false",
            nullable=False
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("hackathon_tasks", "is_archived")
    op.drop_column("contest_tasks", "is_archived")