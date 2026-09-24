"""Enable authenticated outsourcing partners.

Revision ID: 20260923_partner_accounts
Revises: 20260923_wo_started
"""
from alembic import op
import sqlalchemy as sa

revision = "20260923_partner_accounts"
down_revision = "20260923_wo_started"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(sa.text("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'work_partner'"))
    op.add_column("work_partners", sa.Column("user_id", sa.String(), nullable=True))
    op.create_foreign_key("fk_work_partners_user", "work_partners", "users", ["user_id"], ["id"])
    op.create_unique_constraint("uq_work_partners_user", "work_partners", ["user_id"])


def downgrade():
    op.drop_constraint("uq_work_partners_user", "work_partners", type_="unique")
    op.drop_constraint("fk_work_partners_user", "work_partners", type_="foreignkey")
    op.drop_column("work_partners", "user_id")
    # PostgreSQL enum values cannot safely be removed when rows may use the value.
