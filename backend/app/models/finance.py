import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Float, Text, Integer
from sqlalchemy.sql import func
from app.database import Base


class PaymentPurpose(str, enum.Enum):
    lead = "lead"
    investment = "investment"
    service_enquiry = "service_enquiry"
    landowner_settlement = "landowner_settlement"


class PaymentStatus(str, enum.Enum):
    created = "created"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True)
    payer_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    purpose = Column(SAEnum(PaymentPurpose), nullable=False)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=True)
    investment_id = Column(String, ForeignKey("investments.id"), nullable=True)
    work_order_id = Column(String, ForeignKey("work_orders.id"), nullable=True)
    amount_paise = Column(Integer, nullable=False)
    status = Column(SAEnum(PaymentStatus, name="gatewaypaymentstatus"), nullable=False, default=PaymentStatus.created)
    gateway_order_id = Column(String, unique=True, nullable=False)
    gateway_payment_id = Column(String, unique=True, nullable=True)
    gateway_signature = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)


class ExpenseStatus(str, enum.Enum):
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"
    paid = "paid"


class ProjectExpense(Base):
    __tablename__ = "project_expenses"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    work_order_id = Column(String, ForeignKey("work_orders.id"), nullable=True)
    category = Column(String, nullable=False)
    vendor = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    proof_url = Column(String, nullable=True)
    transaction_reference = Column(String, nullable=True)
    status = Column(SAEnum(ExpenseStatus), nullable=False, default=ExpenseStatus.submitted)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)


class SettlementStatus(str, enum.Enum):
    pending_approval = "pending_approval"
    approved = "approved"
    paid = "paid"
    rejected = "rejected"


class LandownerSettlement(Base):
    __tablename__ = "landowner_settlements"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    harvest_id = Column(String, ForeignKey("harvests.id"), nullable=True)
    period_key = Column(String, nullable=False)
    base_amount = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    calculation = Column(Text, nullable=False)
    status = Column(SAEnum(SettlementStatus), nullable=False, default=SettlementStatus.pending_approval)
    approved_by = Column(String, ForeignKey("users.id"), nullable=True)
    payment_id = Column(String, ForeignKey("payments.id"), nullable=True)
    proof_url = Column(String, nullable=True)
    transaction_reference = Column(String, nullable=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)
