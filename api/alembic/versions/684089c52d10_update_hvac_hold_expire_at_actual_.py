"""Update hvac hold expire at actual datatype

Revision ID: 684089c52d10
Revises: cd5eed1da0db
Create Date: 2024-09-23 16:02:27.704292

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '684089c52d10'
down_revision = 'cd5eed1da0db'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('hvac_holds', 'expire_at_actual',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('hvac_holds', 'expire_at_actual',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    # ### end Alembic commands ###
