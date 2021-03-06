"""empty message

Revision ID: 3693e9c1ccf3
Revises: 1ae4039ae567
Create Date: 2014-11-06 23:21:50.821236

"""

# revision identifiers, used by Alembic.
revision = '3693e9c1ccf3'
down_revision = '1ae4039ae567'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('records', sa.Column('case_id', sa.String(length=64), nullable=True))
    op.add_column('records', sa.Column('user_id', sa.String(length=64), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('records', 'user_id')
    op.drop_column('records', 'case_id')
    ### end Alembic commands ###
