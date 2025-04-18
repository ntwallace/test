"""Remove thermostat column for hvac hold

Revision ID: 93ddbd484b20
Revises: fdb924c33627
Create Date: 2024-09-12 19:02:58.194493

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93ddbd484b20'
down_revision = 'fdb924c33627'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('hvac_holds', 'thermostat_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hvac_holds', sa.Column('thermostat_id', sa.UUID(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
