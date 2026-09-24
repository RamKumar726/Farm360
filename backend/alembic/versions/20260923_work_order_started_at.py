"""Record when assigned field work starts.

Revision ID: 20260923_wo_started
Revises: 20260923_proofs
"""
from alembic import op
import sqlalchemy as sa

revision = "20260923_wo_started"
down_revision = "20260923_proofs"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("work_orders", sa.Column("started_at", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column("work_orders", "started_at")
