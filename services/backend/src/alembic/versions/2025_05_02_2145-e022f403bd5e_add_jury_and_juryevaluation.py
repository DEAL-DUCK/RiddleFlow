"""add jury and juryevaluation

Revision ID: e022f403bd5e
Revises: 110efdfc7069
Create Date: 2025-05-02 21:45:31.796155

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "e022f403bd5e"
down_revision: Union[str, None] = "110efdfc7069"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "jurys",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("specialization", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("evaluations_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_jurys_user_id_users"),
            ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_jurys")),
        sa.UniqueConstraint("user_id", name=op.f("uq_jurys_user_id")),
    )

    op.create_table(
        "jury_hackathon_association",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("jury_id", sa.Integer(), nullable=False),
        sa.Column("hackathon_id", sa.Integer(), nullable=False),
        sa.Column(
            "assigned_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["hackathon_id"],
            ["hackathons.id"],
            name=op.f("fk_jury_hackathon_association_hackathon_id_hackathons"),
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["jury_id"],
            ["jurys.id"],
            name=op.f("fk_jury_hackathon_association_jury_id_jurys"),
            ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_jury_hackathon_association")),
    )
    op.create_index(
        "idx_jury_hackathon_unique",
        "jury_hackathon_association",
        ["jury_id", "hackathon_id"],
        unique=True,
    )

    op.create_table(
        "jury_evaluations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("jury_id", sa.Integer(), nullable=False),
        sa.Column("submission_id", sa.Integer(), nullable=False),
        sa.Column("hackathon_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("comment", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["hackathon_id"],
            ["hackathons.id"],
            name=op.f("fk_jury_evaluations_hackathon_id_hackathons"),
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["jury_id"],
            ["jurys.id"],
            name=op.f("fk_jury_evaluations_jury_id_jurys"),
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["hackathon_submissions.id"],
            name=op.f("fk_jury_evaluations_submission_id_hackathon_submissions"),
            ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_jury_evaluations")),
        sa.UniqueConstraint("jury_id", "submission_id", name="uq_jury_submission"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("jury_evaluations")
    op.drop_index(
        "idx_jury_hackathon_unique",
        table_name="jury_hackathon_association"
    )
    op.drop_table("jury_hackathon_association")
    op.drop_table("jurys")