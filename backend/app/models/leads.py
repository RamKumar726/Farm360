import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Boolean, Text, Date, Float, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base



class LeadType(str, enum.Enum):
    site_management = "site_management"
    farm_lease = "farm_lease"
    farm_manage = "farm_manage"
    farm_management = "farm_management"
    one_time_service = "one_time_service"
    investment_interest = "investment_interest"
    service_enquiry = "service_enquiry"
    sell_land = "sell_land"
    land_purchase_interest = "land_purchase_interest"


class LeadSource(str, enum.Enum):
    website = "website"
    digital_marketing = "digital_marketing"
    call_message = "call_message"
    referral = "referral"
    employee = "employee"
    customer_app = "customer_app"


class LeadStatus(str, enum.Enum):
    # Common / Service stages
    prospecting = "prospecting"
    qualification = "qualification"
    need_analysis = "need_analysis"
    value_proposition = "value_proposition"
    decision_makers = "decision_makers"
    proposal_price = "proposal_price"
    negotiation = "negotiation"
    register_user = "register_user"
    login_guide = "login_guide"
    payment = "payment"
    # Lease specific stages
    land_verification = "land_verification"
    feasibility = "feasibility"
    commercial_model = "commercial_model"
    proposal = "proposal"
    agreement = "agreement"
    approval = "approval"
    # Terminal stages
    closed_won = "closed_won"
    closed_lost = "closed_lost"
    # Backward compatibility mappings
    new = "prospecting"
    won = "closed_won"
    lost = "closed_lost"
    completed = "closed_won"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, index=True)
    type = Column(SAEnum(LeadType, native_enum=False), nullable=False)
    source = Column(SAEnum(LeadSource, native_enum=False), nullable=False)
    status = Column(SAEnum(LeadStatus, native_enum=False), nullable=False, default=LeadStatus.prospecting)
    customer_id = Column(String, ForeignKey("users.id"), nullable=True)
    # Existing-customer requests use the Opportunity variant of the same pipeline.
    is_opportunity = Column(Boolean, nullable=False, default=False)
    contact_name = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    crop_name = Column(String, nullable=True)
    farm_location = Column(String, nullable=True)
    farm_area = Column(Float, nullable=True)
    project_level = Column(String, nullable=True)
    lease_arrangement_type = Column(String, nullable=True)
    commercial_model_type = Column(String, nullable=True)
    settlement_base = Column(String, nullable=True)
    fixed_lease_amount = Column(Float, nullable=True)
    revenue_share_percentage = Column(Float, nullable=True)
    lease_duration_months = Column(Integer, nullable=True)
    payment_frequency = Column(String, nullable=True)
    possession_date = Column(Date, nullable=True)
    landowner_responsibilities = Column(Text, nullable=True)
    company_responsibilities = Column(Text, nullable=True)
    termination_conditions = Column(Text, nullable=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    existing_project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    renewal_for_date = Column(Date, nullable=True)
    related_land_sale_id = Column(String, ForeignKey("land_sales.id"), nullable=True)
    employee_id = Column(String, ForeignKey("users.id"), nullable=True)
    assigned_employee_id = Column(String, ForeignKey("users.id"), nullable=True)
    assigned_ao_id = Column(String, ForeignKey("users.id"), nullable=True)
    zone_id = Column(String, ForeignKey("zones.id"), nullable=True)
    branch_id = Column(String, ForeignKey("branches.id"), nullable=True)
    farm_details = Column(Text, nullable=True)

    # Stage Data Payloads (JSON formatted strings)
    qualification_data = Column(Text, nullable=True)
    need_analysis_data = Column(Text, nullable=True)
    value_prop_data = Column(Text, nullable=True)
    land_verification_data = Column(Text, nullable=True)
    ao_feasibility_data = Column(Text, nullable=True)
    commercial_model_data = Column(Text, nullable=True)
    proposal_data = Column(Text, nullable=True)
    negotiation_data = Column(Text, nullable=True)
    agreement_url = Column(String, nullable=True)

    # Solutions, Quotations & Approvals
    ao_quotation_doc = Column(Text, nullable=True)
    is_reviewed_by_employee = Column(Boolean, default=False)
    sent_to_client = Column(Boolean, default=False)
    approval_status = Column(String, default="pending") # pending, approved_zone, approved_founder, rejected

    # Dates & Financials
    services_needed = Column(Text, nullable=True)
    price_to_complete = Column(Float, nullable=True)
    discount_amount = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=True)
    payment_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    site_visit_date = Column(Date, nullable=True)
    advance_paid_date = Column(Date, nullable=True)
    won_date = Column(Date, nullable=True)
    lost_reason = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    customer = relationship("User", foreign_keys=[customer_id])
    employee = relationship("User", foreign_keys=[employee_id])
    assigned_employee = relationship("User", foreign_keys=[assigned_employee_id])
    assigned_ao = relationship("User", foreign_keys=[assigned_ao_id])
    zone = relationship("Zone", back_populates="leads")
    branch = relationship("Branch", foreign_keys=[branch_id])
