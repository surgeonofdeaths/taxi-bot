"""user: chat_id

Revision ID: d82133d0ff09
Revises: e27c735dcf4c
Create Date: 2024-04-26 02:52:50.358575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd82133d0ff09'
down_revision: Union[str, None] = 'e27c735dcf4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('chat_id', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'chat_id')
    # ### end Alembic commands ###
