"""create submissions table

Revision ID: 9dd52ff90723
Revises: 6566b25380a1
Create Date: 2025-04-22 17:00:00.224973

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9dd52ff90723"
down_revision: Union[str, None] = "6566b25380a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "submissions",
        sa.Column("code_url", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "SUBMITTED",
                "GRADED",
                "DISQUALIFIED",
                name="submissionstatus",
            ),
            nullable=False,
        ),
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
        sa.Column("graded_at", sa.DateTime(), nullable=True),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["tasks.id"],
            name=op.f("fk_submissions_task_id_tasks"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_submissions_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_submissions")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("submissions")
