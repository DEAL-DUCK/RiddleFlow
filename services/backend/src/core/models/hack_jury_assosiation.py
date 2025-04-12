from sqlalchemy import Table, Column, ForeignKey
from .base import Base

jury_hackathon_association = Table(
    'jury_hackathon_association',
    Base.metadata,
    Column('jury_id', ForeignKey('jurys.id'), primary_key=True),
    Column('hackathon_id', ForeignKey('hackathons.id'), primary_key=True)
)