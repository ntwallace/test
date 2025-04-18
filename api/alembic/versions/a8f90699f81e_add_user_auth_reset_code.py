"""Add user auth reset code

Revision ID: a8f90699f81e
Revises: 7ae3f34cbc5e
Create Date: 2024-09-06 17:33:16.873698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8f90699f81e'
down_revision = '7ae3f34cbc5e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_auth_reset_codes',
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('reset_code', sa.Uuid(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_auth_reset_codes')
    # ### end Alembic commands ###
