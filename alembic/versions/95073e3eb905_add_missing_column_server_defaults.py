"""add_missing_column_server_defaults

Revision ID: 95073e3eb905
Revises: 9a369873ad71
Create Date: 2026-04-28 00:36:55.524425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95073e3eb905'
down_revision: Union[str, None] = '9a369873ad71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Alembic autogenerate does not detect server_default changes.
    # These ALTER statements add the missing DB-level DEFAULT clauses so that
    # columns are not-null AND have a default even for raw SQL inserts.
    op.alter_column('users', 'is_active',
                    existing_type=sa.Boolean(),
                    server_default=sa.text('true'),
                    existing_nullable=False)

    op.alter_column('conversations', 'title',
                    existing_type=sa.String(length=500),
                    server_default=sa.text("'New Conversation'"),
                    existing_nullable=False)

    op.alter_column('messages', 'tokens_used',
                    existing_type=sa.Integer(),
                    server_default=sa.text('0'),
                    existing_nullable=False)

    op.alter_column('crisis_events', 'resolved',
                    existing_type=sa.Boolean(),
                    server_default=sa.text('false'),
                    existing_nullable=False)


def downgrade() -> None:
    op.alter_column('crisis_events', 'resolved',
                    existing_type=sa.Boolean(),
                    server_default=None,
                    existing_nullable=False)

    op.alter_column('messages', 'tokens_used',
                    existing_type=sa.Integer(),
                    server_default=None,
                    existing_nullable=False)

    op.alter_column('conversations', 'title',
                    existing_type=sa.String(length=500),
                    server_default=None,
                    existing_nullable=False)

    op.alter_column('users', 'is_active',
                    existing_type=sa.Boolean(),
                    server_default=None,
                    existing_nullable=False)
