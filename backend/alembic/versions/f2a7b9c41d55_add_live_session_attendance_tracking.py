"""add live session attendance tracking

Revision ID: f2a7b9c41d55
Revises: c4b6789a2f10
Create Date: 2026-04-19 18:10:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2a7b9c41d55'
down_revision = 'c4b6789a2f10'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('live_sessions', sa.Column('actual_started_at', sa.DateTime(), nullable=True))
    op.add_column('live_sessions', sa.Column('actual_ended_at', sa.DateTime(), nullable=True))

    op.create_table(
        'live_session_attendances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('live_session_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('first_joined_at', sa.DateTime(), nullable=True),
        sa.Column('last_joined_at', sa.DateTime(), nullable=True),
        sa.Column('last_left_at', sa.DateTime(), nullable=True),
        sa.Column('total_duration_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('join_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_present', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['live_session_id'], ['live_sessions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('live_session_id', 'user_id', name='uq_live_session_attendance_session_user'),
    )
    op.create_index(op.f('ix_live_session_attendances_id'), 'live_session_attendances', ['id'], unique=False)
    op.create_index(op.f('ix_live_session_attendances_live_session_id'), 'live_session_attendances', ['live_session_id'], unique=False)
    op.create_index(op.f('ix_live_session_attendances_user_id'), 'live_session_attendances', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_live_session_attendances_user_id'), table_name='live_session_attendances')
    op.drop_index(op.f('ix_live_session_attendances_live_session_id'), table_name='live_session_attendances')
    op.drop_index(op.f('ix_live_session_attendances_id'), table_name='live_session_attendances')
    op.drop_table('live_session_attendances')

    op.drop_column('live_sessions', 'actual_ended_at')
    op.drop_column('live_sessions', 'actual_started_at')
