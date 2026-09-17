"""initial

Revision ID: b6f3ee86a31c
Revises: 
Create Date: 2026-09-15 21:34:02.251439

"""
from alembic import op
import sqlalchemy as sa

revision = 'b6f3ee86a31c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Create branches WITHOUT the FK to users (users does not exist yet)
    op.create_table('branches',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('admin_user_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_branches_id'), 'branches', ['id'], unique=False)

    # Step 2: Create users WITHOUT zone_id FK (zones does not exist yet)
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('founder', 'zone_admin', 'employee', 'agri_officer', 'farm_employee', 'customer', 'real_estate', 'broker', name='userrole'), nullable=False),
        sa.Column('branch_id', sa.String(), nullable=True),
        sa.Column('zone_id', sa.String(), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Step 3: Create zones (branches and users now exist)
    op.create_table('zones',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('branch_id', sa.String(), nullable=False),
        sa.Column('responsible_employee_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id']),
        sa.ForeignKeyConstraint(['responsible_employee_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_zones_id'), 'zones', ['id'], unique=False)

    # Step 4: Now that zones exists, add the remaining FK constraints
    op.create_foreign_key('fk_branches_admin_user', 'branches', 'users', ['admin_user_id'], ['id'])
    op.create_foreign_key('fk_users_zone', 'users', 'zones', ['zone_id'], ['id'])

    # Step 5: All other tables in dependency order
    op.create_table('attendance',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('status', sa.Enum('present', 'absent', 'half_day', 'holiday', 'sunday', name='attendancestatus'), nullable=False),
        sa.Column('replacement_user_id', sa.String(), nullable=True),
        sa.Column('zone_id', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['replacement_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['zone_id'], ['zones.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_attendance_id'), 'attendance', ['id'], unique=False)

    op.create_table('brokers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('contact', sa.String(), nullable=True),
        sa.Column('zone_id', sa.String(), nullable=True),
        sa.Column('assigned_by', sa.String(), nullable=True),
        sa.Column('specializations', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id']),
        sa.ForeignKeyConstraint(['zone_id'], ['zones.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_brokers_id'), 'brokers', ['id'], unique=False)

    op.create_table('customers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('service_type', sa.Enum('one_time', 'managed', 'lease_outsourcing', 'lease_inhouse_complete', 'lease_inhouse_percentage', 'lease_percentage_only', name='servicetype'), nullable=True),
        sa.Column('branch_id', sa.String(), nullable=True),
        sa.Column('zone_id', sa.String(), nullable=True),
        sa.Column('subscription_active', sa.Boolean(), nullable=True),
        sa.Column('subscription_start', sa.Date(), nullable=True),
        sa.Column('subscription_end', sa.Date(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['zone_id'], ['zones.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_customers_id'), 'customers', ['id'], unique=False)

    op.create_table('leads',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('site_management', 'farm_lease', 'farm_manage', 'farm_management', name='leadtype'), nullable=False),
        sa.Column('source', sa.Enum('website', 'digital_marketing', 'call_message', 'referral', 'employee', name='leadsource'), nullable=False),
        sa.Column('status', sa.Enum('new', 'site_visit', 'advance_paid', 'won', 'completed', 'lost', name='leadstatus'), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=True),
        sa.Column('employee_id', sa.String(), nullable=True),
        sa.Column('zone_id', sa.String(), nullable=True),
        sa.Column('branch_id', sa.String(), nullable=True),
        sa.Column('farm_details', sa.Text(), nullable=True),
        sa.Column('site_visit_date', sa.Date(), nullable=True),
        sa.Column('advance_paid_date', sa.Date(), nullable=True),
        sa.Column('won_date', sa.Date(), nullable=True),
        sa.Column('lost_reason', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id']),
        sa.ForeignKeyConstraint(['customer_id'], ['users.id']),
        sa.ForeignKeyConstraint(['employee_id'], ['users.id']),
        sa.ForeignKeyConstraint(['zone_id'], ['zones.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leads_id'), 'leads', ['id'], unique=False)

    op.create_table('notifications',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('new_lead', 'work_order_created', 'work_order_assigned', 'work_order_completed', 'proof_submitted', 'payment_due', 'payment_received', 'prescription_sent', 'visit_scheduled', 'investment_project_posted', 'land_sale_listed', 'partner_accepted', 'partner_rejected', 'visit_completed', 'incident_reported', 'approval_required', 'crop_health_update', 'revenue_credited', name='notificationtype'), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('channel', sa.Enum('in_app', 'whatsapp', 'both', name='notificationchannel'), nullable=False),
        sa.Column('sent_via_whatsapp', sa.Boolean(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)

    op.create_table('projects',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('project_investment', 'agricultural_investment', 'joint_project', name='projecttype'), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('funded_amount', sa.Float(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'open', 'funded', 'active', 'completed', 'settled', name='projectstatus'), nullable=False),
        sa.Column('posted_by', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('total_revenue', sa.Float(), nullable=True),
        sa.Column('cover_image_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['posted_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)

    op.create_table('real_estate_users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('land_details', sa.Text(), nullable=True),
        sa.Column('registration_status', sa.Enum('pending', 'approved', 'rejected', name='registrationstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_real_estate_users_id'), 'real_estate_users', ['id'], unique=False)

    op.create_table('work_partners',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('contact', sa.String(), nullable=True),
        sa.Column('zone_id', sa.String(), nullable=True),
        sa.Column('work_types', sa.JSON(), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'blacklisted', name='workpartnerstatus'), nullable=False),
        sa.Column('payment_terms', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['zone_id'], ['zones.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_work_partners_id'), 'work_partners', ['id'], unique=False)

    op.create_table('farms',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('area', sa.Float(), nullable=True),
        sa.Column('gps_lat', sa.Float(), nullable=True),
        sa.Column('gps_lng', sa.Float(), nullable=True),
        sa.Column('soil_type', sa.String(), nullable=True),
        sa.Column('water_source', sa.String(), nullable=True),
        sa.Column('zone_id', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['zone_id'], ['zones.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_farms_id'), 'farms', ['id'], unique=False)

    op.create_table('investments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('project_id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('project', 'agricultural', 'joint_project', name='investmenttype'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('bond_period', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'active', 'locked', 'completed', 'settled', name='investmentstatus'), nullable=False),
        sa.Column('revenue_share_percentage', sa.Float(), nullable=True),
        sa.Column('expected_return', sa.Float(), nullable=True),
        sa.Column('actual_return', sa.Float(), nullable=True),
        sa.Column('settlement_date', sa.Date(), nullable=True),
        sa.Column('agreement_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_investments_id'), 'investments', ['id'], unique=False)

    op.create_table('land_sales',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=True),
        sa.Column('real_estate_user_id', sa.String(), nullable=True),
        sa.Column('land_type', sa.Enum('agricultural', 'residential', 'commercial', 'industrial', 'mixed', name='landtype'), nullable=False),
        sa.Column('area', sa.Float(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('facing', sa.String(), nullable=True),
        sa.Column('gps_lat', sa.Float(), nullable=True),
        sa.Column('gps_lng', sa.Float(), nullable=True),
        sa.Column('listed_price', sa.Float(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'site_visit', 'quoted', 'listed', 'broadcast', 'interested', 'agreement', 'registered', 'sold', 'cancelled', name='landsalestatus'), nullable=False),
        sa.Column('broker_ids', sa.JSON(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('photos', sa.JSON(), nullable=True),
        sa.Column('listed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sold_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['real_estate_user_id'], ['real_estate_users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_land_sales_id'), 'land_sales', ['id'], unique=False)

    op.create_table('agreements',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('farm_id', sa.String(), nullable=True),
        sa.Column('type', sa.Enum('one_time', 'managed', 'lease', 'investment', name='agreementtype'), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('payment_terms', sa.Text(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'active', 'completed', 'cancelled', name='agreementstatus'), nullable=False),
        sa.Column('document_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agreements_id'), 'agreements', ['id'], unique=False)

    op.create_table('crop_designs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('farm_id', sa.String(), nullable=False),
        sa.Column('agri_officer_id', sa.String(), nullable=False),
        sa.Column('best_practices', sa.Text(), nullable=True),
        sa.Column('land_suitability', sa.Text(), nullable=True),
        sa.Column('timing', sa.Text(), nullable=True),
        sa.Column('crop_time', sa.Text(), nullable=True),
        sa.Column('estimated_yearly_cost', sa.Float(), nullable=True),
        sa.Column('intercrop_design', sa.Text(), nullable=True),
        sa.Column('recommended_machines', sa.Text(), nullable=True),
        sa.Column('research_notes', sa.Text(), nullable=True),
        sa.Column('approval_status', sa.Enum('pending', 'approved', 'rejected', name='approvalstatus'), nullable=False),
        sa.Column('approved_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['agri_officer_id'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crop_designs_id'), 'crop_designs', ['id'], unique=False)

    op.create_table('work_orders',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('farm_id', sa.String(), nullable=False),
        sa.Column('agri_officer_id', sa.String(), nullable=True),
        sa.Column('type', sa.Enum('cleaning', 'securing', 'irrigation', 'electric', 'harvest', 'soil_water_test', 'cropping', 'land_leveling', 'pruning', 'fertilizer_pestcontrol', 'monitoring', 'construction', name='workordertype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'assigned', 'partner_accepted', 'in_progress', 'completed', 'verified', 'failed', name='workorderstatus'), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('outsourcing_partner_id', sa.String(), nullable=True),
        sa.Column('farm_employee_id', sa.String(), nullable=True),
        sa.Column('payment_status', sa.Enum('pending', 'partial', 'paid', 'reduced', name='paymentstatus'), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['agri_officer_id'], ['users.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['farm_employee_id'], ['users.id']),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id']),
        sa.ForeignKeyConstraint(['outsourcing_partner_id'], ['work_partners.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_work_orders_id'), 'work_orders', ['id'], unique=False)

    op.create_table('crop_cycles',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('crop_design_id', sa.String(), nullable=False),
        sa.Column('farm_id', sa.String(), nullable=False),
        sa.Column('cycle_name', sa.String(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('auto_generated', sa.Boolean(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['crop_design_id'], ['crop_designs.id']),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crop_cycles_id'), 'crop_cycles', ['id'], unique=False)

    op.create_table('prescriptions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('farm_id', sa.String(), nullable=False),
        sa.Column('agri_officer_id', sa.String(), nullable=False),
        sa.Column('work_order_id', sa.String(), nullable=True),
        sa.Column('prescription_text', sa.Text(), nullable=False),
        sa.Column('quote_amount', sa.Float(), nullable=True),
        sa.Column('sent_to', sa.JSON(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'sent', 'approved', 'rejected', name='prescriptionstatus'), nullable=False),
        sa.Column('attachment_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['agri_officer_id'], ['users.id']),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id']),
        sa.ForeignKeyConstraint(['work_order_id'], ['work_orders.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prescriptions_id'), 'prescriptions', ['id'], unique=False)

    op.create_table('visits',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('work_order_id', sa.String(), nullable=True),
        sa.Column('farm_id', sa.String(), nullable=True),
        sa.Column('farm_employee_id', sa.String(), nullable=False),
        sa.Column('type', sa.Enum('new_lead_visit', 'auto_visit', 'assign_visit', 'sale_visit', 'random_visit', name='visittype'), nullable=False),
        sa.Column('gps_lat', sa.Float(), nullable=True),
        sa.Column('gps_lng', sa.Float(), nullable=True),
        sa.Column('proof_photos', sa.JSON(), nullable=True),
        sa.Column('proof_video_url', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'completed', 'failed', name='visitstatus'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('visited_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['farm_employee_id'], ['users.id']),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id']),
        sa.ForeignKeyConstraint(['work_order_id'], ['work_orders.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_visits_id'), 'visits', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_visits_id'), table_name='visits')
    op.drop_table('visits')
    op.drop_index(op.f('ix_prescriptions_id'), table_name='prescriptions')
    op.drop_table('prescriptions')
    op.drop_index(op.f('ix_crop_cycles_id'), table_name='crop_cycles')
    op.drop_table('crop_cycles')
    op.drop_index(op.f('ix_work_orders_id'), table_name='work_orders')
    op.drop_table('work_orders')
    op.drop_index(op.f('ix_crop_designs_id'), table_name='crop_designs')
    op.drop_table('crop_designs')
    op.drop_index(op.f('ix_agreements_id'), table_name='agreements')
    op.drop_table('agreements')
    op.drop_index(op.f('ix_land_sales_id'), table_name='land_sales')
    op.drop_table('land_sales')
    op.drop_index(op.f('ix_investments_id'), table_name='investments')
    op.drop_table('investments')
    op.drop_index(op.f('ix_farms_id'), table_name='farms')
    op.drop_table('farms')
    op.drop_index(op.f('ix_work_partners_id'), table_name='work_partners')
    op.drop_table('work_partners')
    op.drop_index(op.f('ix_real_estate_users_id'), table_name='real_estate_users')
    op.drop_table('real_estate_users')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
    op.drop_index(op.f('ix_leads_id'), table_name='leads')
    op.drop_table('leads')
    op.drop_index(op.f('ix_customers_id'), table_name='customers')
    op.drop_table('customers')
    op.drop_index(op.f('ix_brokers_id'), table_name='brokers')
    op.drop_table('brokers')
    op.drop_index(op.f('ix_attendance_id'), table_name='attendance')
    op.drop_table('attendance')
    op.drop_constraint('fk_users_zone', 'users', type_='foreignkey')
    op.drop_constraint('fk_branches_admin_user', 'branches', type_='foreignkey')
    op.drop_index(op.f('ix_zones_id'), table_name='zones')
    op.drop_table('zones')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_branches_id'), table_name='branches')
    op.drop_table('branches')
    # Drop custom enum types
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='attendancestatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='servicetype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='leadtype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='leadsource').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='leadstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='notificationtype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='notificationchannel').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='projecttype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='projectstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='registrationstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='workpartnerstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='investmenttype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='investmentstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='landtype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='landsalestatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='agreementtype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='agreementstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='approvalstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='workordertype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='workorderstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='paymentstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='visittype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='visitstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='prescriptionstatus').drop(op.get_bind(), checkfirst=True)
