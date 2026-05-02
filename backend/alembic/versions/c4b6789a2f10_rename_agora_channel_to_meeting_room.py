"""rename agora channel to meeting room

Revision ID: c4b6789a2f10
Revises: a5e13e4b31a6
Create Date: 2026-04-19 16:40:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4b6789a2f10'
down_revision = '26740c98c9f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('live_sessions') as batch_op:
        batch_op.alter_column(
            'agora_channel_name',
            new_column_name='meeting_room_name',
            existing_type=sa.String(),
            existing_nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table('live_sessions') as batch_op:
        batch_op.alter_column(
            'meeting_room_name',
            new_column_name='agora_channel_name',
            existing_type=sa.String(),
            existing_nullable=True,
        )