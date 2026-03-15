"""live_session_course_id_nullable

Revision ID: a5e13e4b31a6
Revises: 376154e6df8f
Create Date: 2026-03-15 03:04:54.075838

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5e13e4b31a6'
down_revision = '376154e6df8f'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('live_sessions', 'course_id',
               existing_type=sa.INTEGER(),
               nullable=True)


def downgrade():
    op.alter_column('live_sessions', 'course_id',
               existing_type=sa.INTEGER(),
               nullable=False)
