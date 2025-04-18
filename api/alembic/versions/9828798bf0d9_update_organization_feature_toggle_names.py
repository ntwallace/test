"""Update organization feature toggle names

Revision ID: 9828798bf0d9
Revises: 3ca00ab02893
Create Date: 2024-09-04 19:18:02.904365

"""
from alembic import op
import sqlalchemy as sa
from alembic_postgresql_enum import TableReference

# revision identifiers, used by Alembic.
revision = '9828798bf0d9'
down_revision = '3ca00ab02893'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.sync_enum_values('public', 'organizationfeaturetoggleenum', ['alert-center', 'autoconfigure', 'manual-overrides', 'autochangeover', 'zone-temperatures'],
                        [TableReference(table_schema='public', table_name='organization_feature_toggles', column_name='organization_feature_toggle')],
                        enum_values_to_rename=[])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.sync_enum_values('public', 'organizationfeaturetoggleenum', ['alert_center', 'auto_configure', 'manual_overrides', 'auto_changeover', 'zone_temperatures'],
                        [TableReference(table_schema='public', table_name='organization_feature_toggles', column_name='organization_feature_toggle')],
                        enum_values_to_rename=[])
    # ### end Alembic commands ###
