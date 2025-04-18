"""Rename electricity dashboards table

Revision ID: 664a276d82a2
Revises: d15420435015
Create Date: 2024-12-27 21:30:15.714186

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '664a276d82a2'
down_revision = 'd15420435015'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.rename_table('electric_dashboards', 'electricity_dashboards')
    op.alter_column('electricity_dashboards', 'electric_dashboard_id', new_column_name='electricity_dashboard_id')
    op.execute('ALTER INDEX electric_dashboards_pkey RENAME TO electricity_dashboards_pkey')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.rename_table('electricity_dashboards', 'electric_dashboards')
    op.alter_column('electric_dashboards', 'electricity_dashboard_id', new_column_name='electric_dashboard_id')
    op.execute('ALTER INDEX electricity_dashboards_pkey RENAME TO electric_dashboards_pkey')
    # ### end Alembic commands ###
