"""create profiles table

Revision ID: 83a78f70e59d
Revises: 71a0a39dd22c
Create Date: 2025-04-22 16:44:54.490872

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "83a78f70e59d"
down_revision: Union[str, None] = "71a0a39dd22c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "profiles",
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("logo_url", sa.String(length=255), nullable=True),
        sa.Column("bio", sa.String(length=1000), nullable=True),
        sa.Column("country", sa.String(length=30), nullable=True),
        sa.Column("city", sa.String(length=30), nullable=True),
        sa.Column("job", sa.String(length=50), nullable=True),
        sa.Column("phone_number", sa.String(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_profiles_user_id_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_profiles")),
        sa.UniqueConstraint("phone_number", name=op.f("uq_profiles_phone_number")),
        sa.UniqueConstraint("user_id", name=op.f("uq_profiles_user_id")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("profiles")
