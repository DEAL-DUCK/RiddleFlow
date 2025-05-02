"""add jury and juryevaluation

Revision ID: c1b9b6d43e84
Revises: 110efdfc7069
Create Date: 2025-05-02 19:21:10.525510

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c1b9b6d43e84"
down_revision: Union[str, None] = "110efdfc7069"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем таблицу jurys
    op.create_table(
        'jurys',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('specialization', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('evaluations_count', sa.Integer(), default=0, nullable=False),
    )

    # Создаем таблицу jury_evaluations
    op.create_table(
        'jury_evaluations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('jury_id', sa.Integer(), sa.ForeignKey('jurys.id', ondelete='CASCADE')),
        sa.Column('submission_id', sa.Integer(), sa.ForeignKey('hackathon_submissions.id', ondelete='CASCADE')),
        sa.Column('hackathon_id', sa.Integer(), sa.ForeignKey('hackathons.id', ondelete='CASCADE')),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('comment', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint('jury_id', 'submission_id', name='uq_jury_submission'),
    )

    # Создаем таблицу для связи многие-ко-многим между jurys и hackathons
    op.create_table(
        'jury_hackathon_association',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('jury_id', sa.Integer(), sa.ForeignKey('jurys.id', ondelete='CASCADE')),
        sa.Column('hackathon_id', sa.Integer(), sa.ForeignKey('hackathons.id', ondelete='CASCADE')),
        sa.Column('assigned_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Index('idx_jury_hackathon_unique', 'jury_id', 'hackathon_id', unique=True),
    )

    # Добавляем индекс для улучшения производительности запросов
    op.create_index(op.f('ix_jurys_user_id'), 'jurys', ['user_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем индексы
    op.drop_index(op.f('ix_jurys_user_id'), table_name='jurys')

    # Удаляем таблицы в обратном порядке
    op.drop_table('jury_hackathon_association')
    op.drop_table('jury_evaluations')
    op.drop_table('jurys')