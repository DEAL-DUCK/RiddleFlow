"""add archive hackathon

Revision ID: 4fa26ce3c2ba
Revises: e91189f7f83f
Create Date: 2025-05-01 22:48:09.850521

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "4fa26ce3c2ba"
down_revision: Union[str, None] = "e91189f7f83f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Проверяем существование типа перед созданием
    conn = op.get_bind()
    type_exists = conn.execute(
        sa.text("SELECT 1 FROM pg_type WHERE typname = 'hackathonstatus'")
    ).scalar()

    if not type_exists:
        hackathon_status = postgresql.ENUM(
            'PLANNED', 'ACTIVE', 'COMPLETED', 'CANCELED',
            name='hackathonstatus'
        )
        hackathon_status.create(op.get_bind())

    # Создаем таблицу archived_hackathons с foreign key в обратном направлении
    op.create_table(
        'archived_hackathons',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('original_hackathon_id', sa.Integer(), sa.ForeignKey('hackathons.id', ondelete="CASCADE"),
                  unique=True),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=900), nullable=False),
        sa.Column('original_status', postgresql.ENUM(
            'PLANNED', 'ACTIVE', 'COMPLETED', 'CANCELED',
            name='hackathonstatus',
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

        # Индексы
        sa.Index('idx_archived_hackathon_creator', 'creator_id'),
        sa.Index('idx_archived_hackathon_time', 'archived_at'),
    )

    # Добавляем foreign key для связи one-to-one в обратном направлении
    # (это безопаснее, так как archived_hackathons может быть пустой)
    op.create_foreign_key(
        'fk_archived_hackathon_original',
        'archived_hackathons', 'hackathons',
        ['original_hackathon_id'], ['id'],
        ondelete="CASCADE"
    )


def downgrade() -> None:
    # Удаляем foreign key связи
    op.drop_constraint('fk_archived_hackathon_original', 'archived_hackathons', type_='foreignkey')

    # Удаляем таблицу archived_hackathons
    op.drop_table('archived_hackathons')

    # Проверяем, используется ли тип в других таблицах перед удалением
    conn = op.get_bind()
    type_used = conn.execute(
        sa.text("""
            SELECT 1 FROM pg_attribute 
            WHERE atttypid = (SELECT oid FROM pg_type WHERE typname = 'hackathonstatus') 
            LIMIT 1
        """)
    ).scalar()

    if not type_used:
        op.execute("DROP TYPE IF EXISTS hackathonstatus")