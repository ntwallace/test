"""Remove unique constraint from gateway name

Revision ID: 7ae3f34cbc5e
Revises: 9828798bf0d9
Create Date: 2024-09-04 19:53:22.537891

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ae3f34cbc5e'
down_revision = '9828798bf0d9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('gateways_name_key', 'gateways', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('gateways_name_key', 'gateways', ['name'])
    # ### end Alembic commands ###
