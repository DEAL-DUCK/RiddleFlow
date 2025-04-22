"""create hackathon_user_associations table

Revision ID: 84bdb346d0d4
Revises: 5b29de299a42
Create Date: 2025-04-22 16:53:40.241888

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "84bdb346d0d4"
down_revision: Union[str, None] = "5b29de299a42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "hackathon_user_association",
        sa.Column("hackathon_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "user_status",
            sa.Enum(
                "REGISTERED",
                "COMPLETED",
                "DISQUALIFIED",
                "REFUSED",
                name="participationstatus",
            ),
            server_default="REGISTERED",
            nullable=False,
        ),
        sa.Column(
            "registration_date",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("tasks_completed", sa.Integer(), nullable=False),
        sa.Column("points_earned", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["hackathon_id"],
            ["hackathons.id"],
            name=op.f("fk_hackathon_user_association_hackathon_id_hackathons"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_hackathon_user_association_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_hackathon_user_association")),
        sa.UniqueConstraint(
            "hackathon_id", "user_id", name="idx_unique_hackathon_user"
        ),
    )
    op.create_index(
        "idx_hackathon_user_user_id",
        "hackathon_user_association",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("idx_hackathon_user_user_id", table_name="hackathon_user_association")
    op.drop_table("hackathon_user_association")
