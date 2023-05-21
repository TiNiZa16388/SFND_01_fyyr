"""empty message

Revision ID: 58805083d3b9
Revises: 8bed4ffa4a9f
Create Date: 2023-05-21 17:55:56.563067

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '58805083d3b9'
down_revision = '8bed4ffa4a9f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('website', sa.String(), nullable=True))
        batch_op.drop_column('website_link')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.add_column(sa.Column('website_link', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.drop_column('website')

    # ### end Alembic commands ###
