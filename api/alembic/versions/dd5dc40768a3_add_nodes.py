"""Add nodes

Revision ID: dd5dc40768a3
Revises: 3f48cb6cd8ae
Create Date: 2024-06-13 18:15:14.482215

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd5dc40768a3'
down_revision = '3f48cb6cd8ae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('nodes',
    sa.Column('node_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('duid', sa.String(length=255), nullable=False),
    sa.Column('type', sa.String(length=255), nullable=False),
    sa.Column('gateway_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('node_id'),
    sa.UniqueConstraint('duid'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('nodes')
    # ### end Alembic commands ###
