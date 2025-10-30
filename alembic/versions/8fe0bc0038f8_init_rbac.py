"""init rbac

Revision ID: 8fe0bc0038f8
Revises: 
Create Date: 2025-10-30 10:58:02.168458

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8fe0bc0038f8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Roles
    op.create_table(
        'roles',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('name', name='uq_roles_name'),
    )
    op.create_index('ix_roles_name', 'roles', ['name'], unique=True)

    # Permissions
    op.create_table(
        'permissions',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('resource', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.UniqueConstraint('name', name='uq_permissions_name'),
    )
    op.create_index('ix_permissions_name', 'permissions', ['name'], unique=True)
    op.create_index('ix_permissions_resource', 'permissions', ['resource'], unique=False)
    op.create_index('ix_permissions_action', 'permissions', ['action'], unique=False)

    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('username', name='uq_users_username'),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Association: user_roles
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('role_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_user_roles_user_id', 'user_roles', ['user_id'], unique=False)
    op.create_index('ix_user_roles_role_id', 'user_roles', ['role_id'], unique=False)

    # Association: role_permissions
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.String(length=36), nullable=False),
        sa.Column('permission_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_role_permissions_role_id', 'role_permissions', ['role_id'], unique=False)
    op.create_index('ix_role_permissions_permission_id', 'role_permissions', ['permission_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_role_permissions_permission_id', table_name='role_permissions')
    op.drop_index('ix_role_permissions_role_id', table_name='role_permissions')
    op.drop_table('role_permissions')

    op.drop_index('ix_user_roles_role_id', table_name='user_roles')
    op.drop_index('ix_user_roles_user_id', table_name='user_roles')
    op.drop_table('user_roles')

    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')

    op.drop_index('ix_permissions_action', table_name='permissions')
    op.drop_index('ix_permissions_resource', table_name='permissions')
    op.drop_index('ix_permissions_name', table_name='permissions')
    op.drop_table('permissions')

    op.drop_index('ix_roles_name', table_name='roles')
    op.drop_table('roles')
