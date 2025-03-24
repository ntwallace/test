"""Add temperature unit widgets

Revision ID: b1a025954a9d
Revises: 5b5eb7f9d21a
Create Date: 2024-07-12 23:56:00.401126

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b1a025954a9d'
down_revision = '5b5eb7f9d21a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('Fridge', 'Freezer', 'Other', name='appliancetype').create(op.get_bind())
    op.create_table('temperature_unit_widgets',
    sa.Column('temperature_unit_widget_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('low_c', sa.Float(), nullable=False),
    sa.Column('high_c', sa.Float(), nullable=False),
    sa.Column('alert_threshold_s', sa.Integer(), nullable=False),
    sa.Column('appliance_type', postgresql.ENUM('Fridge', 'Freezer', 'Other', name='appliancetype', create_type=False), nullable=False),
    sa.Column('temperature_place_id', sa.Uuid(), nullable=False),
    sa.Column('temperature_dashboard_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('temperature_unit_widget_id', 'temperature_place_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('temperature_unit_widgets')
    sa.Enum('Fridge', 'Freezer', 'Other', name='appliancetype').drop(op.get_bind())
    # ### end Alembic commands ###
