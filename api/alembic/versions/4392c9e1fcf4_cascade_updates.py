"""cascade updates

Revision ID: 4392c9e1fcf4
Revises: 93ddbd484b20
Create Date: 2024-09-13 22:08:55.760877

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4392c9e1fcf4'
down_revision = '93ddbd484b20'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('control_zone_hvac_widgets_friday_schedule_id_fkey', 'control_zone_hvac_widgets', type_='foreignkey')
    op.drop_constraint('control_zone_hvac_widgets_saturday_schedule_id_fkey', 'control_zone_hvac_widgets', type_='foreignkey')
    op.drop_constraint('control_zone_hvac_widgets_sunday_schedule_id_fkey', 'control_zone_hvac_widgets', type_='foreignkey')
    op.drop_constraint('control_zone_hvac_widgets_tuesday_schedule_id_fkey', 'control_zone_hvac_widgets', type_='foreignkey')
    op.drop_constraint('control_zone_hvac_widgets_monday_schedule_id_fkey', 'control_zone_hvac_widgets', type_='foreignkey')
    op.drop_constraint('control_zone_hvac_widgets_wednesday_schedule_id_fkey', 'control_zone_hvac_widgets', type_='foreignkey')
    op.drop_constraint('control_zone_hvac_widgets_thursday_schedule_id_fkey', 'control_zone_hvac_widgets', type_='foreignkey')
    op.create_foreign_key(None, 'control_zone_hvac_widgets', 'hvac_schedules', ['tuesday_schedule_id'], ['hvac_schedule_id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'control_zone_hvac_widgets', 'hvac_schedules', ['friday_schedule_id'], ['hvac_schedule_id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'control_zone_hvac_widgets', 'hvac_schedules', ['monday_schedule_id'], ['hvac_schedule_id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'control_zone_hvac_widgets', 'hvac_schedules', ['thursday_schedule_id'], ['hvac_schedule_id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'control_zone_hvac_widgets', 'hvac_schedules', ['wednesday_schedule_id'], ['hvac_schedule_id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'control_zone_hvac_widgets', 'hvac_schedules', ['saturday_schedule_id'], ['hvac_schedule_id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'control_zone_hvac_widgets', 'hvac_schedules', ['sunday_schedule_id'], ['hvac_schedule_id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'control_zone_hvac_widgets', type_='foreignkey')
    op.drop_constraint(None, 'control_zone_hvac_widgets', type_='foreignkey')
    op.drop_constraint(None, 'control_zone_hvac_widgets', type_='foreignkey')
    op.drop_constraint(None, 'control_zone_hvac_widgets', type_='foreignkey')
    op.drop_constraint(None, 'control_zone_hvac_widgets', type_='foreignkey')
    op.drop_constraint(None, 'control_zone_hvac_widgets', type_='foreignkey')
    op.drop_constraint(None, 'control_zone_hvac_widgets', type_='foreignkey')
    op.create_foreign_key('control_zone_hvac_widgets_thursday_schedule_id_fkey', 'control_zone_hvac_widgets', 'hvac_schedules', ['thursday_schedule_id'], ['hvac_schedule_id'])
    op.create_foreign_key('control_zone_hvac_widgets_wednesday_schedule_id_fkey', 'control_zone_hvac_widgets', 'hvac_schedules', ['wednesday_schedule_id'], ['hvac_schedule_id'])
    op.create_foreign_key('control_zone_hvac_widgets_monday_schedule_id_fkey', 'control_zone_hvac_widgets', 'hvac_schedules', ['monday_schedule_id'], ['hvac_schedule_id'])
    op.create_foreign_key('control_zone_hvac_widgets_tuesday_schedule_id_fkey', 'control_zone_hvac_widgets', 'hvac_schedules', ['tuesday_schedule_id'], ['hvac_schedule_id'])
    op.create_foreign_key('control_zone_hvac_widgets_sunday_schedule_id_fkey', 'control_zone_hvac_widgets', 'hvac_schedules', ['sunday_schedule_id'], ['hvac_schedule_id'])
    op.create_foreign_key('control_zone_hvac_widgets_saturday_schedule_id_fkey', 'control_zone_hvac_widgets', 'hvac_schedules', ['saturday_schedule_id'], ['hvac_schedule_id'])
    op.create_foreign_key('control_zone_hvac_widgets_friday_schedule_id_fkey', 'control_zone_hvac_widgets', 'hvac_schedules', ['friday_schedule_id'], ['hvac_schedule_id'])
    # ### end Alembic commands ###
