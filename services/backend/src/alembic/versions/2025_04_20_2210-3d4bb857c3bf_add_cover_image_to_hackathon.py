"""add_cover_image_to_hackathon

Revision ID: 3d4bb857c3bf
Revises: 1268f699210b
Create Date: 2025-04-20 22:10:25.780004

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3d4bb857c3bf"
down_revision: Union[str, None] = "1268f699210b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        'hackathons',
        sa.Column('cover_image', sa.String(255), nullable=True)
    )

def downgrade():
    op.drop_column('hackathons', 'cover_image')
