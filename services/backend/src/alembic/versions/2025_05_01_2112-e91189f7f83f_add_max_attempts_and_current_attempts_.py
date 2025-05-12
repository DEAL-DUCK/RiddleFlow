"""add max_attempts and current_attempts to contest_tasks

Revision ID: e91189f7f83f
Revises: 5b265eef9239
Create Date: 2025-05-01 21:12:17.607250

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e91189f7f83f"
down_revision: Union[str, None] = "5b265eef9239"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "contest_tasks",
        sa.Column("max_attempts", sa.Integer(), server_default="5", nullable=False)
    )
    op.add_column(
        "contest_tasks",
        sa.Column("current_attempts", sa.Integer(), server_default="0", nullable=False)
    )
    op.alter_column("contest_tasks", "max_attempts", server_default=None)
    op.alter_column("contest_tasks", "current_attempts", server_default=None)


def downgrade() -> None:
    op.drop_column("contest_tasks", "current_attempts")
    op.drop_column("contest_tasks", "max_attempts")