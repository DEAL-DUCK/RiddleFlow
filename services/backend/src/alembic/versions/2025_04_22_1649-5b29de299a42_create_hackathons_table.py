"""create hackathons table

Revision ID: 5b29de299a42
Revises: 96948db87b25
Create Date: 2025-04-22 16:49:51.876828

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5b29de299a42"
down_revision: Union[str, None] = "96948db87b25"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "hackathons",
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=900), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "hackathon_status",
            sa.Enum(
                "PLANNED",
                "ACTIVE",
                "COMPLETED",
                "CANCELED",
                name="hackathonstatus",
            ),
            server_default="PLANNED",
            nullable=False,
        ),
        sa.Column("max_participants", sa.Integer(), nullable=False),
        sa.Column(
            "current_participants",
            sa.Integer(),
            server_default="0",
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
            name=op.f("fk_hackathons_creator_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_hackathons")),
        sa.UniqueConstraint("title", name=op.f("uq_hackathons_title")),
    )
    op.create_index(
        "idx_hackathon_status",
        "hackathons",
        ["hackathon_status"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_hackathon_status", table_name="hackathons")
    op.drop_table("hackathons")
