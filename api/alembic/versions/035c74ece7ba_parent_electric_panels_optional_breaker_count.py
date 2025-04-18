"""parent electric panels and optional breaker count

Revision ID: 035c74ece7ba
Revises: b3a480f5157a
Create Date: 2024-08-07 22:22:17.025826

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '035c74ece7ba'
down_revision = 'b3a480f5157a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('electric_panels', sa.Column('parent_electric_panel_id', sa.Uuid(), nullable=True))
    op.alter_column('electric_panels', 'breaker_count',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('electric_panels', 'breaker_count',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('electric_panels', 'parent_electric_panel_id')
    # ### end Alembic commands ###
