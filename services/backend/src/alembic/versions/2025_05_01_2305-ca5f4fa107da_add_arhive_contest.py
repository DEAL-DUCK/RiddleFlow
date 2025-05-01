"""add archive contest

Revision ID: 5fb37ce4d3cb
Revises: 4fa26ce3c2ba
Create Date: 2025-05-02 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5fb37ce4d3cb"
down_revision: Union[str, None] = "4fa26ce3c2ba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Проверяем существование типа conteststatus
    conn = op.get_bind()
    type_exists = conn.execute(
        sa.text("SELECT 1 FROM pg_type WHERE typname = 'conteststatus'")
    ).scalar()

    if not type_exists:
        contest_status = postgresql.ENUM(
            'PLANNED', 'ACTIVE', 'COMPLETED', 'CANCELED',
            name='conteststatus'
        )
        contest_status.create(op.get_bind())

    # Создаем таблицу archived_contests
    op.create_table(
        'archived_contests',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('original_contest_id', sa.Integer(),
                  sa.ForeignKey('contests.id', ondelete="CASCADE"),
                  unique=True),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=900), nullable=False),
        sa.Column('original_status', postgresql.ENUM(
            'PLANNED', 'ACTIVE', 'COMPLETED', 'CANCELED',
            name='conteststatus',
            create_type=False
        ), nullable=False),
        sa.Column('max_participants', sa.Integer(), nullable=False),
        sa.Column('current_participants', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('allow_teams', sa.Boolean(), nullable=False),
        sa.Column('logo_url', sa.String(length=255), nullable=True),
        sa.Column('archived_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('archive_reason', sa.String(length=255), nullable=True),
        sa.Column('archived_by_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('creator_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),

        sa.Index('idx_archived_contest_creator', 'creator_id'),
        sa.Index('idx_archived_contest_time', 'archived_at'),
    )


def downgrade() -> None:
    # Удаляем таблицу archived_contests
    op.drop_table('archived_contests')

    # Проверяем, используется ли тип в других таблицах перед удалением
    conn = op.get_bind()
    type_used = conn.execute(
        sa.text("""
            SELECT 1 FROM pg_attribute 
            WHERE atttypid = (SELECT oid FROM pg_type WHERE typname = 'conteststatus') 
            LIMIT 1
        """)
    ).scalar()

    if not type_used:
        op.execute("DROP TYPE IF EXISTS conteststatus")