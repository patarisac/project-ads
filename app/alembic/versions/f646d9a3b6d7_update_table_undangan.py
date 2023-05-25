"""update table undangan

Revision ID: f646d9a3b6d7
Revises: 91842cdfbe33
Create Date: 2023-05-20 13:14:09.924755

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f646d9a3b6d7'
down_revision = '91842cdfbe33'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('undangan', sa.Column('creator', sa.String(), nullable=False))
    op.drop_column('undangan', 'creator_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('undangan', sa.Column('creator_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('undangan', 'creator')
    # ### end Alembic commands ###