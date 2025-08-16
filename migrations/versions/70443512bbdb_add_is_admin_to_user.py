"""add is_admin to user

Revision ID: 70443512bbdb
Revises: 75d110b216f3
Create Date: 2025-08-15 20:17:07.479717

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70443512bbdb'
down_revision = '75d110b216f3'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'is_admin',
                sa.Boolean(),
                nullable=False,
                server_default=sa.false()   # <- backfills existing rows as 0/False
            )
        )
    # (optional) drop the server default after backfill; SQLite supports this via batch copy
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('is_admin', server_default=None)

    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_admin')

    # ### end Alembic commands ###
