"""create hackathon_submissions table

Revision ID: 86d69ce50d90
Revises: 4e9f9f53389d
Create Date: 2025-05-01 12:20:02.438557

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "86d69ce50d90"
down_revision: Union[str, None] = "4e9f9f53389d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "hackathon_submissions",
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
            ["hackathon_tasks.id"],
            name=op.f("fk_hackathon_submissions_task_id_hackathon_tasks"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_hackathon_submissions_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_hackathon_submissions")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("hackathon_submissions")
    # ### end Alembic commands ###
