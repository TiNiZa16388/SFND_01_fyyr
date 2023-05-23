"""empty message

Revision ID: 11cfc69fd369
Revises: 9304eed171ba
Create Date: 2023-05-23 00:17:08.628809

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '11cfc69fd369'
down_revision = '9304eed171ba'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.drop_column('seeking_talent')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.add_column(sa.Column('seeking_talent', sa.BOOLEAN(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
