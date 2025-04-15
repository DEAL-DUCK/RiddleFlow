"""create group_user_associations table

Revision ID: 027af0cddaa7
Revises: f41ea6acec8d
Create Date: 2025-04-15 10:25:19.804455

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "027af0cddaa7"
down_revision: Union[str, None] = "f41ea6acec8d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "group_user_association",
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
            name=op.f("fk_group_user_association_group_id_groups"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_group_user_association_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_group_user_association")),
        sa.UniqueConstraint("group_id", "user_id", name="idx_unique_group_user"),
    )
    op.create_index(
        "idx_group_user_user_id",
        "group_user_association",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_group_user_user_id", table_name="group_user_association")
    op.drop_table("group_user_association")
