"""create access_tokens table

Revision ID: 6566b25380a1
Revises: 844cc0e2bb51
Create Date: 2025-04-22 16:57:59.960624

"""

from typing import Sequence, Union
import fastapi_users_db_sqlalchemy
from alembic import op
import sqlalchemy as sa


revision: str = "6566b25380a1"
down_revision: Union[str, None] = "844cc0e2bb51"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "accesstokens",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=43), nullable=False),
        sa.Column(
            "created_at",
            fastapi_users_db_sqlalchemy.generics.TIMESTAMPAware(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_accesstokens_user_id_users"),
            ondelete="cascade",
        ),
        sa.PrimaryKeyConstraint("token", name=op.f("pk_accesstokens")),
    )
    op.create_index(
        op.f("ix_accesstokens_created_at"),
        "accesstokens",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_accesstokens_created_at"), table_name="accesstokens")
    op.drop_table("accesstokens")
