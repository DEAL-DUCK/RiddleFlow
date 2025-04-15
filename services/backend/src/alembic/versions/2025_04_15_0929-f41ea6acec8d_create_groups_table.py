"""create groups table

Revision ID: f41ea6acec8d
Revises: cb48b7e0fd8f
Create Date: 2025-04-15 09:29:45.739235

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f41ea6acec8d"
down_revision: Union[str, None] = "cb48b7e0fd8f"
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
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("max_members", sa.Integer(), nullable=False),
        sa.Column("current_members", sa.Integer(), server_default="0", nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"], ["users.id"], name=op.f("fk_groups_owner_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_groups")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("groups")
