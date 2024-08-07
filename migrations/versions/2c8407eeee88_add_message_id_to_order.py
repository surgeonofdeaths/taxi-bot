"""add message_id to order

Revision ID: 2c8407eeee88
Revises: c0dfb2a2fc4d
Create Date: 2024-05-08 16:18:59.430606

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c8407eeee88'
down_revision: Union[str, None] = 'c0dfb2a2fc4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('message_id', sa.Integer(), nullable=False))
    op.drop_column('orders', 'price')
    op.drop_column('orders', 'car_mark')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('orders', sa.Column('car_mark', sa.CHAR(length=256), autoincrement=False, nullable=True))
    op.add_column('orders', sa.Column('price', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('orders', 'message_id')
    # ### end Alembic commands ###
