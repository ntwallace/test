"""Add api key access scopes tables

Revision ID: d15420435015
Revises: 9ca75a48a32a
Create Date: 2024-11-08 06:37:03.606154

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd15420435015'
down_revision = '9ca75a48a32a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('api_key_access_roles',
    sa.Column('api_key_id', sa.Uuid(), nullable=False),
    sa.Column('access_role_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('api_key_id', 'access_role_id')
    )
    op.create_table('api_key_access_scopes',
    sa.Column('api_key_id', sa.Uuid(), nullable=False),
    sa.Column('access_scope', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('api_key_id', 'access_scope')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('api_key_access_scopes')
    op.drop_table('api_key_access_roles')
    # ### end Alembic commands ###
