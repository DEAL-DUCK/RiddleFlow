"""tasks table

Revision ID: 844cc0e2bb51
Revises: 499e672f1340
Create Date: 2025-04-22 16:57:05.883225

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "844cc0e2bb51"
down_revision: Union[str, None] = "499e672f1340"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tasks",
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "task_type",
            sa.Enum(
                "CODING",
                "QUIZ",
                "DESIGN",
                "DATA_SCIENCE",
                "HARDWARE",
                name="tasktype",
            ),
            nullable=False,
        ),
        sa.Column("hackathon_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["hackathon_id"],
            ["hackathons.id"],
            name=op.f("fk_tasks_hackathon_id_hackathons"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tasks")),
    )
    op.create_index("idx_task_hackathon", "tasks", ["hackathon_id"], unique=False)
    op.create_index(
        "idx_task_type", "tasks", ["task_type", "hackathon_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_task_type", table_name="tasks")
    op.drop_index("idx_task_hackathon", table_name="tasks")
    op.drop_table("tasks")
