"""correct updated_at field for all models

Revision ID: c0dfb2a2fc4d
Revises: ef54f7702a5b
Create Date: 2024-05-06 19:50:38.165662

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0dfb2a2fc4d'
down_revision: Union[str, None] = 'ef54f7702a5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
