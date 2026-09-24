"""Persist workflow, payments, expenses and lease settlements.

Revision ID: 20260923_workflows
Revises: 0f62da97919e
"""
from alembic import op
import sqlalchemy as sa

revision = "20260923_workflows"
down_revision = "0f62da97919e"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for column in ("type", "source", "status"):
            op.execute(sa.text(f"ALTER TABLE leads ALTER COLUMN {column} TYPE VARCHAR USING {column}::text"))
        op.execute(sa.text("UPDATE leads SET status = CASE status WHEN 'new' THEN 'prospecting' WHEN 'site_visit' THEN 'decision_makers' WHEN 'advance_paid' THEN 'payment' WHEN 'won' THEN 'closed_won' WHEN 'completed' THEN 'closed_won' WHEN 'lost' THEN 'closed_lost' ELSE status END"))
        for value in ("one_time_service", "managing_farm", "lease", "land_sale"):
            op.execute(sa.text(f"ALTER TYPE projecttype ADD VALUE IF NOT EXISTS '{value}'"))
        for value in ("not_started", "started", "in_progress", "almost_completed"):
            op.execute(sa.text(f"ALTER TYPE projectstatus ADD VALUE IF NOT EXISTS '{value}'"))
        for value in ("proof_submitted", "customer_accepted"):
            op.execute(sa.text(f"ALTER TYPE workorderstatus ADD VALUE IF NOT EXISTS '{value}'"))
        op.execute(sa.text("ALTER TYPE workordertype ADD VALUE IF NOT EXISTS 'land_sale_followup'"))

    op.add_column("leads", sa.Column("is_opportunity", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("leads", sa.Column("contact_name", sa.String(), nullable=True))
    op.add_column("leads", sa.Column("contact_phone", sa.String(), nullable=True))
    op.add_column("leads", sa.Column("contact_email", sa.String(), nullable=True))
    op.add_column("leads", sa.Column("assigned_employee_id", sa.String(), nullable=True))
    op.create_foreign_key("fk_leads_assigned_employee", "leads", "users", ["assigned_employee_id"], ["id"])
    op.add_column("leads", sa.Column("crop_name", sa.String(), nullable=True))
    op.add_column("leads", sa.Column("farm_location", sa.String(), nullable=True))
    op.add_column("leads", sa.Column("farm_area", sa.Float(), nullable=True))
    op.add_column("leads", sa.Column("project_level", sa.String(), nullable=True))
    op.add_column("leads", sa.Column("lease_arrangement_type", sa.String(), nullable=True))
    op.add_column("leads", sa.Column("commercial_model_type", sa.String(), nullable=True))
    op.add_column("leads", sa.Column("settlement_base", sa.String(), nullable=True))
    op.add_column("leads", sa.Column("fixed_lease_amount", sa.Float(), nullable=True))
    op.add_column("leads", sa.Column("revenue_share_percentage", sa.Float(), nullable=True))
    op.add_column("leads", sa.Column("lease_duration_months", sa.Integer(), nullable=True))
    op.add_column("leads", sa.Column("payment_frequency", sa.String(), nullable=True))
    op.add_column("leads", sa.Column("possession_date", sa.Date(), nullable=True))
    op.add_column("leads", sa.Column("landowner_responsibilities", sa.Text(), nullable=True))
    op.add_column("leads", sa.Column("company_responsibilities", sa.Text(), nullable=True))
    op.add_column("leads", sa.Column("termination_conditions", sa.Text(), nullable=True))
    op.add_column("leads", sa.Column("project_id", sa.String(), nullable=True))
    op.add_column("leads", sa.Column("existing_project_id", sa.String(), nullable=True))
    op.add_column("leads", sa.Column("renewal_for_date", sa.Date(), nullable=True))
    op.add_column("leads", sa.Column("related_land_sale_id", sa.String(), nullable=True))
    op.add_column("leads", sa.Column("payment_confirmed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key("fk_leads_project", "leads", "projects", ["project_id"], ["id"])
    op.create_foreign_key("fk_leads_existing_project", "leads", "projects", ["existing_project_id"], ["id"])
    op.create_foreign_key("fk_leads_land_sale", "leads", "land_sales", ["related_land_sale_id"], ["id"])
    op.add_column("agreements", sa.Column("lead_id", sa.String(), nullable=True))
    op.add_column("agreements", sa.Column("project_id", sa.String(), nullable=True))
    op.create_foreign_key("fk_agreements_lead", "agreements", "leads", ["lead_id"], ["id"])
    op.create_foreign_key("fk_agreements_project", "agreements", "projects", ["project_id"], ["id"])
    op.add_column("brokers", sa.Column("user_id", sa.String(), nullable=True))
    op.create_foreign_key("fk_brokers_user", "brokers", "users", ["user_id"], ["id"])
    op.create_unique_constraint("uq_brokers_user_id", "brokers", ["user_id"])

    op.add_column("projects", sa.Column("minimum_investment", sa.Float(), nullable=False, server_default="150000"))
    op.add_column("projects", sa.Column("crop_name", sa.String(), nullable=True))
    op.add_column("projects", sa.Column("subscription_end", sa.Date(), nullable=True))
    op.add_column("projects", sa.Column("assigned_ao_id", sa.String(), nullable=True))
    op.add_column("projects", sa.Column("prototype_id", sa.String(), nullable=True))
    op.create_foreign_key("fk_projects_assigned_ao", "projects", "users", ["assigned_ao_id"], ["id"])
    op.create_foreign_key("fk_projects_prototype", "projects", "prototypes", ["prototype_id"], ["id"])
    op.create_index("uq_projects_lead_id", "projects", ["lead_id"], unique=True)
    op.add_column("investments", sa.Column("minimum_amount_snapshot", sa.Float(), nullable=True))
    op.add_column("investments", sa.Column("payout_reference", sa.String(), nullable=True))
    op.add_column("investments", sa.Column("payout_proof_url", sa.String(), nullable=True))
    op.add_column("investments", sa.Column("lead_id", sa.String(), nullable=True))
    op.create_foreign_key("fk_investments_lead", "investments", "leads", ["lead_id"], ["id"])

    op.alter_column("work_orders", "farm_id", existing_type=sa.String(), nullable=True)
    op.add_column("work_orders", sa.Column("lead_id", sa.String(), nullable=True))
    op.create_foreign_key("fk_work_orders_lead", "work_orders", "leads", ["lead_id"], ["id"])
    op.add_column("work_orders", sa.Column("assigned_employee_id", sa.String(), nullable=True))
    op.create_foreign_key("fk_work_orders_assigned_employee", "work_orders", "users", ["assigned_employee_id"], ["id"])

    op.create_table(
        "payments",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("payer_user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("purpose", sa.Enum("lead", "investment", "service_enquiry", "landowner_settlement", name="paymentpurpose"), nullable=False),
        sa.Column("lead_id", sa.String(), sa.ForeignKey("leads.id"), nullable=True),
        sa.Column("investment_id", sa.String(), sa.ForeignKey("investments.id"), nullable=True),
        sa.Column("work_order_id", sa.String(), sa.ForeignKey("work_orders.id"), nullable=True),
        sa.Column("amount_paise", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("created", "paid", "failed", "refunded", name="gatewaypaymentstatus"), nullable=False, server_default="created"),
        sa.Column("gateway_order_id", sa.String(), nullable=False, unique=True),
        sa.Column("gateway_payment_id", sa.String(), nullable=True, unique=True),
        sa.Column("gateway_signature", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_payments_id", "payments", ["id"])

    op.create_table(
        "project_expenses",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("project_id", sa.String(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("work_order_id", sa.String(), sa.ForeignKey("work_orders.id"), nullable=True),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("vendor", sa.String(), nullable=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("proof_url", sa.String(), nullable=True),
        sa.Column("transaction_reference", sa.String(), nullable=True),
        sa.Column("status", sa.Enum("submitted", "approved", "rejected", "paid", name="expensestatus"), nullable=False, server_default="submitted"),
        sa.Column("created_by", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_project_expenses_id", "project_expenses", ["id"])

    op.create_table(
        "outsourcing_contracts",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("project_id", sa.String(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("work_order_id", sa.String(), sa.ForeignKey("work_orders.id"), nullable=True),
        sa.Column("partner_id", sa.String(), sa.ForeignKey("work_partners.id"), nullable=False),
        sa.Column("scope", sa.Text(), nullable=False),
        sa.Column("terms", sa.Text(), nullable=True),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("document_url", sa.String(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.Enum("active", "completed", "cancelled", name="outsourcingcontractstatus"), nullable=False, server_default="active"),
        sa.Column("created_by", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_outsourcing_contracts_id", "outsourcing_contracts", ["id"])

    op.create_table(
        "landowner_settlements",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("project_id", sa.String(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("harvest_id", sa.String(), sa.ForeignKey("harvests.id"), nullable=True),
        sa.Column("period_key", sa.String(), nullable=False),
        sa.Column("base_amount", sa.Float(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("calculation", sa.Text(), nullable=False),
        sa.Column("status", sa.Enum("pending_approval", "approved", "paid", "rejected", name="settlementstatus"), nullable=False, server_default="pending_approval"),
        sa.Column("approved_by", sa.String(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("payment_id", sa.String(), sa.ForeignKey("payments.id"), nullable=True),
        sa.Column("proof_url", sa.String(), nullable=True),
        sa.Column("transaction_reference", sa.String(), nullable=True),
        sa.Column("created_by", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_landowner_settlements_id", "landowner_settlements", ["id"])
    op.create_unique_constraint("uq_settlement_project_period", "landowner_settlements", ["project_id", "period_key"])
    op.add_column("harvests", sa.Column("buyer_name", sa.String(), nullable=True))
    op.add_column("harvests", sa.Column("sale_reference", sa.String(), nullable=True))
    op.add_column("harvests", sa.Column("is_revenue_received", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("harvests", sa.Column("revenue_payment_reference", sa.String(), nullable=True))
    op.add_column("harvests", sa.Column("revenue_received_at", sa.DateTime(timezone=True), nullable=True))
    op.execute(sa.text("UPDATE harvests SET is_revenue_received = TRUE WHERE gross_revenue IS NOT NULL AND gross_revenue > 0"))


def downgrade():
    op.drop_index("ix_outsourcing_contracts_id", table_name="outsourcing_contracts")
    op.drop_table("outsourcing_contracts")
    op.drop_column("harvests", "revenue_received_at")
    op.drop_column("harvests", "revenue_payment_reference")
    op.drop_column("harvests", "is_revenue_received")
    op.drop_column("harvests", "sale_reference")
    op.drop_column("harvests", "buyer_name")
    op.drop_constraint("uq_settlement_project_period", "landowner_settlements", type_="unique")
    op.drop_index("ix_landowner_settlements_id", table_name="landowner_settlements")
    op.drop_table("landowner_settlements")
    op.drop_index("ix_project_expenses_id", table_name="project_expenses")
    op.drop_table("project_expenses")
    op.drop_index("ix_payments_id", table_name="payments")
    op.drop_table("payments")
    op.drop_constraint("uq_brokers_user_id", "brokers", type_="unique")
    op.drop_constraint("fk_brokers_user", "brokers", type_="foreignkey")
    op.drop_column("brokers", "user_id")
    op.drop_constraint("fk_agreements_project", "agreements", type_="foreignkey")
    op.drop_constraint("fk_agreements_lead", "agreements", type_="foreignkey")
    op.drop_column("agreements", "project_id")
    op.drop_column("agreements", "lead_id")
    op.drop_constraint("fk_work_orders_lead", "work_orders", type_="foreignkey")
    op.drop_column("work_orders", "lead_id")
    op.drop_constraint("fk_work_orders_assigned_employee", "work_orders", type_="foreignkey")
    op.drop_column("work_orders", "assigned_employee_id")
    op.alter_column("work_orders", "farm_id", existing_type=sa.String(), nullable=False)
    op.drop_index("uq_projects_lead_id", table_name="projects")
    op.drop_constraint("fk_projects_assigned_ao", "projects", type_="foreignkey")
    op.drop_constraint("fk_projects_prototype", "projects", type_="foreignkey")
    op.drop_column("projects", "prototype_id")
    op.drop_column("projects", "assigned_ao_id")
    op.drop_column("projects", "subscription_end")
    op.drop_column("projects", "crop_name")
    op.drop_column("projects", "minimum_investment")
    op.drop_column("investments", "minimum_amount_snapshot")
    op.drop_column("investments", "payout_proof_url")
    op.drop_column("investments", "payout_reference")
    op.drop_constraint("fk_investments_lead", "investments", type_="foreignkey")
    op.drop_column("investments", "lead_id")
    op.drop_constraint("fk_leads_existing_project", "leads", type_="foreignkey")
    op.drop_constraint("fk_leads_project", "leads", type_="foreignkey")
    op.drop_constraint("fk_leads_land_sale", "leads", type_="foreignkey")
    op.drop_column("leads", "payment_confirmed_at")
    op.drop_column("leads", "existing_project_id")
    op.drop_column("leads", "renewal_for_date")
    op.drop_column("leads", "related_land_sale_id")
    op.drop_column("leads", "project_id")
    op.drop_column("leads", "contact_email")
    op.drop_column("leads", "farm_area")
    op.drop_column("leads", "farm_location")
    op.drop_constraint("fk_leads_assigned_employee", "leads", type_="foreignkey")
    op.drop_column("leads", "assigned_employee_id")
    op.drop_column("leads", "contact_phone")
    op.drop_column("leads", "crop_name")
    for column in ("project_level", "lease_arrangement_type", "commercial_model_type", "settlement_base", "fixed_lease_amount", "revenue_share_percentage", "lease_duration_months", "payment_frequency", "possession_date", "landowner_responsibilities", "company_responsibilities", "termination_conditions"):
        op.drop_column("leads", column)
    op.drop_column("leads", "contact_name")
    op.drop_column("leads", "is_opportunity")
