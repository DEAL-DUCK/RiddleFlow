"""create groups table

Revision ID: 96948db87b25
Revises: 83a78f70e59d
Create Date: 2025-04-22 16:47:59.144513

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "96948db87b25"
down_revision: Union[str, None] = "83a78f70e59d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "groups",
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column(
            "type",
            sa.Enum("TEAM", "JURY", name="grouptype"),
            server_default="TEAM",
            nullable=False,
        ),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("max_members", sa.Integer(), nullable=False),
        sa.Column("current_members", sa.Integer(), server_default="0", nullable=False),
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
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "INACTIVE", "BANNED", name="groupstatus"),
            server_default="ACTIVE",
            nullable=False,
        ),
        sa.Column("logo_url", sa.String(length=255), nullable=True),
        sa.Column("social_media_links", sa.Text(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["users.id"], name=op.f("fk_groups_owner_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_groups")),
        sa.UniqueConstraint("title", name=op.f("uq_groups_title")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("groups")
