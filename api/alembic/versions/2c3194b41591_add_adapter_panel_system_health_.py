"""Add adapter panel system health electric widgets

Revision ID: 2c3194b41591
Revises: 1e5c53345116
Create Date: 2024-07-16 14:58:50.806583

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c3194b41591'
down_revision = '1e5c53345116'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('panel_system_health_electric_widget',
    sa.Column('electric_widget_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('electric_dashboard_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('electric_widget_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('panel_system_health_electric_widget')
    # ### end Alembic commands ###
