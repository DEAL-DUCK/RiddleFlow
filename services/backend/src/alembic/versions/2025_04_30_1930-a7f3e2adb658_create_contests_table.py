"""create contests table

Revision ID: a7f3e2adb658
Revises: 9dd52ff90723
Create Date: 2025-04-30 19:30:38.060357

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7f3e2adb658"
down_revision: Union[str, None] = "9dd52ff90723"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "contests",
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=900), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "contest_status",
            sa.Enum(
                "PLANNED",
                "ACTIVE",
                "COMPLETED",
                "CANCELED",
                name="conteststatus",
            ),
            server_default="PLANNED",
            nullable=False,
        ),
        sa.Column("max_participants", sa.Integer(), nullable=False),
        sa.Column(
            "current_participants",
            sa.Integer(),
            server_default="1",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("allow_teams", sa.Boolean(), nullable=False),
        sa.Column("creator_id", sa.Integer(), nullable=False),
        sa.Column("logo_url", sa.String(length=255), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["users.id"],
            name=op.f("fk_contests_creator_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_contests")),
        sa.UniqueConstraint("title", name=op.f("uq_contests_title")),
    )
    op.create_index("idx_contests_status", "contests", ["contest_status"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_contests_status", table_name="contests")
    op.drop_table("contests")
