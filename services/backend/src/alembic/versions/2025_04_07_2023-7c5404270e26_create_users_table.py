"""create users table

Revision ID: 7c5404270e26
Revises:
Create Date: 2025-04-07 20:23:43.237242

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7c5404270e26"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TYPE IF EXISTS userrole")
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("username", sa.String(length=40), nullable=False),
        sa.Column(
            "user_role",
            sa.Enum("PARTICIPANT", "CREATOR", name="userrole"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=1024), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_index("idx_user_username", "users", ["username"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index("idx_user_username", table_name="users")
    op.drop_table("users")
