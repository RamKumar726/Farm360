import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Float, Integer, Date, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base



class InvestmentType(str, enum.Enum):
    project = "project"
    agricultural = "agricultural"
    joint_project = "joint_project"


class InvestmentStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    locked = "locked"
    completed = "completed"
    settled = "settled"


class InvestmentVerificationStage(str, enum.Enum):
    showed_interest = "showed_interest"
    employee_contacted = "employee_contacted"
    customer_approved = "customer_approved"
    site_visit = "site_visit"
    agreemented = "agreemented"
    zone_approved = "zone_approved"
    founder_approved = "founder_approved"
    payment_gateway = "payment_gateway"
    completed = "completed"


class Investment(Base):
    __tablename__ = "investments"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=True)
    type = Column(SAEnum(InvestmentType), nullable=False)
    amount = Column(Float, nullable=False)
    proposed_amount = Column(Float, nullable=True)
    questions = Column(Text, nullable=True)
    acknowledgement_accepted = Column(Boolean, default=False)
    bond_period = Column(Integer, nullable=True)   # in months
    status = Column(SAEnum(InvestmentStatus), nullable=False, default=InvestmentStatus.pending)
    verification_stage = Column(SAEnum(InvestmentVerificationStage), nullable=False, default=InvestmentVerificationStage.showed_interest)
    revenue_share_percentage = Column(Float, nullable=True)
    expected_return = Column(Float, nullable=True)
    actual_return = Column(Float, nullable=True)
    settlement_date = Column(Date, nullable=True)
    payout_reference = Column(String, nullable=True)
    payout_proof_url = Column(String, nullable=True)
    minimum_amount_snapshot = Column(Float, nullable=True)
    agreement_url = Column(String, nullable=True)  # Cloudinary URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    project = relationship("Project", back_populates="investments")
    customer = relationship("Customer", back_populates="investments")
