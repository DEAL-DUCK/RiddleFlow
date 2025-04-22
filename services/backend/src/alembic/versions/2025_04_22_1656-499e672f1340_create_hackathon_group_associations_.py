"""create hackathon_group_associations table

Revision ID: 499e672f1340
Revises: af14f27d5885
Create Date: 2025-04-22 16:56:19.009221

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "499e672f1340"
down_revision: Union[str, None] = "af14f27d5885"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "hackathon_group_association",
        sa.Column("hackathon_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column(
            "group_status",
            sa.Enum(
                "REGISTERED",
                "COMPLETED",
                "DISQUALIFIED",
                "REFUSED",
                name="teamstatus",
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
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
            name=op.f("fk_hackathon_group_association_group_id_groups"),
        ),
        sa.ForeignKeyConstraint(
            ["hackathon_id"],
            ["hackathons.id"],
            name=op.f("fk_hackathon_group_association_hackathon_id_hackathons"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_hackathon_group_association")),
        sa.UniqueConstraint(
            "hackathon_id", "group_id", name="idx_unique_hackathon_group"
        ),
    )
    op.create_index(
        "idx_hackathon_group_group_id",
        "hackathon_group_association",
        ["group_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "idx_hackathon_group_group_id",
        table_name="hackathon_group_association",
    )
    op.drop_table("hackathon_group_association")
