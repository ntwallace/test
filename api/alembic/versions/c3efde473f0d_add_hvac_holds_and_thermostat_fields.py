"""Add hvac holds and thermostat fields

Revision ID: c3efde473f0d
Revises: 4ac2fe81068e
Create Date: 2024-07-23 19:19:55.769884

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c3efde473f0d'
down_revision = '4ac2fe81068e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('Auto', 'AlwaysOn', name='hvacfanmode').create(op.get_bind())
    sa.Enum('Auto', 'AlwaysOn', name='thermostathvacfanmode').create(op.get_bind())
    sa.Enum('Locked', 'Unlocked', name='thermostatlockouttype').create(op.get_bind())
    op.create_table('hvac_holds',
    sa.Column('hvac_hold_id', sa.Uuid(), nullable=False),
    sa.Column('control_zone_hvac_widget_id', sa.Uuid(), nullable=False),
    sa.Column('mode', postgresql.ENUM('cooling', 'heating', 'auto', 'off', name='hvacschedulemode', create_type=False), nullable=False),
    sa.Column('author', sa.String(), nullable=False),
    sa.Column('fan_mode', postgresql.ENUM('Auto', 'AlwaysOn', name='hvacfanmode', create_type=False), nullable=False),
    sa.Column('set_point_c', sa.Float(), nullable=True),
    sa.Column('set_point_auto_heating_c', sa.Float(), nullable=True),
    sa.Column('set_point_auto_cooling_c', sa.Float(), nullable=True),
    sa.Column('expire_at_estimated', sa.DateTime(), nullable=False),
    sa.Column('expire_at_actual', sa.DateTime(), nullable=False),
    sa.Column('thermostat_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('hvac_hold_id')
    )
    op.add_column('control_zone_hvac_widgets', sa.Column('hvac_zone_id', sa.Uuid(), nullable=False))
    op.add_column('thermostats', sa.Column('keypad_lockout', postgresql.ENUM('Locked', 'Unlocked', name='thermostatlockouttype', create_type=False), nullable=False))
    op.add_column('thermostats', sa.Column('fan_mode', postgresql.ENUM('Auto', 'AlwaysOn', name='thermostathvacfanmode', create_type=False), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('thermostats', 'fan_mode')
    op.drop_column('thermostats', 'keypad_lockout')
    op.drop_column('control_zone_hvac_widgets', 'hvac_zone_id')
    op.drop_table('hvac_holds')
    sa.Enum('Locked', 'Unlocked', name='thermostatlockouttype').drop(op.get_bind())
    sa.Enum('Auto', 'AlwaysOn', name='thermostathvacfanmode').drop(op.get_bind())
    sa.Enum('Auto', 'AlwaysOn', name='hvacfanmode').drop(op.get_bind())
    # ### end Alembic commands ###
