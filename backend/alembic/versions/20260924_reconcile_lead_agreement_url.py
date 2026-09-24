"""Ensure the lead agreement URL field exists in databases stamped at 0f62da97919e.

Revision ID: 20260924_lead_agreement
Revises: 20260923_partner_accounts
"""
from alembic import op
import sqlalchemy as sa


revision = "20260924_lead_agreement"
down_revision = "20260923_partner_accounts"
branch_labels = None
depends_on = None


def upgrade():
    # Some databases were already stamped at 0f62da97919e before that revision
    # included agreement_url. Keep this forward repair safe on databases where
    # the column is already present.
    op.execute(sa.text("ALTER TABLE leads ADD COLUMN IF NOT EXISTS agreement_url VARCHAR"))


def downgrade():
    # Keep this compatibility repair non-destructive: the column may have
    # existed before this revision was applied on another database.
    pass
