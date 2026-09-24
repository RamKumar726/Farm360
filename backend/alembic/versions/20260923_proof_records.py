"""Persist proof submissions and verification history per work order.

Revision ID: 20260923_proofs
Revises: 20260923_services
"""
from alembic import op
import sqlalchemy as sa

revision = "20260923_proofs"
down_revision = "20260923_services"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "proofs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("work_order_id", sa.String(), sa.ForeignKey("work_orders.id"), nullable=False),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("submitted_by", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("reviewed_by", sa.String(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_status", sa.String(), nullable=False, server_default="submitted"),
    )
    op.create_index("ix_proofs_work_order_id", "proofs", ["work_order_id"])


def downgrade():
    op.drop_index("ix_proofs_work_order_id", table_name="proofs")
    op.drop_table("proofs")
