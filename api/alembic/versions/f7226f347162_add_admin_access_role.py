"""add admin access role

Revision ID: f7226f347162
Revises: 664a276d82a2
Create Date: 2025-01-22 17:03:25.955843

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy.orm import Session

from app.v1.auth.models.access_role import AccessRole
from app.v1.auth.models.access_role_access_scope import AccessRoleAccessScope
from app.v1.schemas import AccessScope


# revision identifiers, used by Alembic.
revision = 'f7226f347162'
down_revision = '664a276d82a2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        # Create a new AccessRole
        access_role = AccessRole(name="admin:admin")
        session.add(access_role)
        session.flush()  # Flush to get the generated ID
        session.refresh(access_role)

        # Loop over AccessScope enum and create AccessRoleAccessScope entries
        for scope in AccessScope:
            access_scope_entry = AccessRoleAccessScope(
                access_role_id=access_role.access_role_id, access_scope=scope
            )
            session.add(access_scope_entry)

        # Commit the transaction
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        # Remove the AccessRole and its associated AccessRoleAccessScope entries
        access_role = (
            session.query(AccessRole).filter(AccessRole.name == "admin:admin").first()
        )
        if access_role:
            session.query(AccessRoleAccessScope).filter(
                AccessRoleAccessScope.access_role_id == access_role.access_role_id
            ).delete()
            session.delete(access_role)

        # Commit the transaction
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    # ### end Alembic commands ###
