"""Enterprise payment events, quote versions and audit trail.

Revision ID: 20261001_enterprise
Revises: 20260924_lead_agreement
"""

from alembic import op
import sqlalchemy as sa


revision = "20261001_enterprise"
down_revision = "20260924_lead_agreement"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "quote_versions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("lead_id", sa.String(), sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="INR"),
        sa.Column("subtotal_paise", sa.Integer(), nullable=False),
        sa.Column("discount_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tax_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_paise", sa.Integer(), nullable=False),
        sa.Column("inclusions", sa.Text()),
        sa.Column("exclusions", sa.Text()),
        sa.Column("timeline_assumptions", sa.Text()),
        sa.Column("terms", sa.Text()),
        sa.Column("valid_until", sa.DateTime(timezone=True)),
        sa.Column("created_by", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("approved_by", sa.String(), sa.ForeignKey("users.id")),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("superseded_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("lead_id", "version_number", name="uq_quote_lead_version"),
    )
    op.create_index("ix_quote_versions_lead_id", "quote_versions", ["lead_id"])
    op.create_index("ix_quote_versions_status", "quote_versions", ["status"])

    op.create_table(
        "quote_items",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("quote_version_id", sa.String(), sa.ForeignKey("quote_versions.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("quantity_milli", sa.Integer(), nullable=False, server_default="1000"),
        sa.Column("unit", sa.String(), nullable=False, server_default="item"),
        sa.Column("unit_price_paise", sa.Integer(), nullable=False),
        sa.Column("line_total_paise", sa.Integer(), nullable=False),
        sa.Column("internal_cost_paise", sa.Integer()),
    )
    op.create_index("ix_quote_items_quote_version_id", "quote_items", ["quote_version_id"])

    op.create_table(
        "quote_acceptances",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("quote_version_id", sa.String(), sa.ForeignKey("quote_versions.id"), nullable=False, unique=True),
        sa.Column("customer_user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("accepted_total_paise", sa.Integer(), nullable=False),
        sa.Column("accepted_terms_snapshot", sa.Text()),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "invoices",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("invoice_number", sa.String(), nullable=False, unique=True),
        sa.Column("customer_user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("lead_id", sa.String(), sa.ForeignKey("leads.id")),
        sa.Column("quote_version_id", sa.String(), sa.ForeignKey("quote_versions.id"), nullable=False, unique=True),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="INR"),
        sa.Column("subtotal_paise", sa.Integer(), nullable=False),
        sa.Column("discount_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tax_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_paise", sa.Integer(), nullable=False),
        sa.Column("paid_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(), nullable=False, server_default="issued"),
        sa.Column("notes", sa.Text()),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("due_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_invoices_invoice_number", "invoices", ["invoice_number"], unique=True)
    op.create_index("ix_invoices_customer_user_id", "invoices", ["customer_user_id"])
    op.create_index("ix_invoices_lead_id", "invoices", ["lead_id"])
    op.create_index("ix_invoices_status", "invoices", ["status"])
    op.create_table(
        "invoice_lines",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("invoice_id", sa.String(), sa.ForeignKey("invoices.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("quantity_milli", sa.Integer(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("unit_price_paise", sa.Integer(), nullable=False),
        sa.Column("line_total_paise", sa.Integer(), nullable=False),
    )
    op.create_index("ix_invoice_lines_invoice_id", "invoice_lines", ["invoice_id"])

    op.add_column("payments", sa.Column("quote_version_id", sa.String(), sa.ForeignKey("quote_versions.id")))
    op.add_column("payments", sa.Column("invoice_id", sa.String(), nullable=True))
    op.add_column("payments", sa.Column("currency", sa.String(length=3), nullable=False, server_default="INR"))
    op.add_column("payments", sa.Column("refunded_amount_paise", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("payments", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))

    op.create_table(
        "payment_webhook_events",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("payload_sha256", sa.String(), nullable=False),
        sa.Column("signature_valid", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("processing_error", sa.Text()),
        sa.Column("gateway_order_id", sa.String()),
        sa.Column("gateway_payment_id", sa.String()),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("processed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_payment_webhook_events_event_type", "payment_webhook_events", ["event_type"])
    op.create_index("ix_payment_webhook_events_gateway_order_id", "payment_webhook_events", ["gateway_order_id"])
    op.create_index("ix_payment_webhook_events_gateway_payment_id", "payment_webhook_events", ["gateway_payment_id"])

    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("actor_user_id", sa.String(), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", sa.String(), nullable=False),
        sa.Column("reason", sa.Text()),
        sa.Column("change_summary", sa.Text()),
        sa.Column("correlation_id", sa.String()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    for column in ("actor_user_id", "action", "entity_type", "entity_id", "correlation_id"):
        op.create_index(f"ix_audit_events_{column}", "audit_events", [column])

    op.create_table(
        "payment_allocations",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("payment_id", sa.String(), sa.ForeignKey("payments.id"), nullable=False),
        sa.Column("invoice_id", sa.String(), sa.ForeignKey("invoices.id"), nullable=False),
        sa.Column("amount_paise", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("payment_id", "invoice_id", name="uq_payment_invoice_allocation"),
    )
    op.create_index("ix_payment_allocations_payment_id", "payment_allocations", ["payment_id"])
    op.create_index("ix_payment_allocations_invoice_id", "payment_allocations", ["invoice_id"])

    op.create_foreign_key("fk_payments_invoice_id", "payments", "invoices", ["invoice_id"], ["id"])


def downgrade():
    op.drop_constraint("fk_payments_invoice_id", "payments", type_="foreignkey")
    op.drop_table("payment_allocations")
    op.drop_table("audit_events")
    op.drop_table("payment_webhook_events")
    op.drop_column("payments", "updated_at")
    op.drop_column("payments", "refunded_amount_paise")
    op.drop_column("payments", "currency")
    op.drop_column("payments", "quote_version_id")
    op.drop_column("payments", "invoice_id")
    op.drop_table("invoice_lines")
    op.drop_table("invoices")
    op.drop_table("quote_acceptances")
    op.drop_table("quote_items")
    op.drop_table("quote_versions")
