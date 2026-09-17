import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Boolean, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class LeadType(str, enum.Enum):
    site_management = "site_management"
    farm_lease = "farm_lease"
    farm_manage = "farm_manage"
    farm_management = "farm_management"


class LeadSource(str, enum.Enum):
    website = "website"
    digital_marketing = "digital_marketing"
    call_message = "call_message"
    referral = "referral"
    employee = "employee"


class LeadStatus(str, enum.Enum):
    new = "new"
    site_visit = "site_visit"
    advance_paid = "advance_paid"
    won = "won"
    completed = "completed"
    lost = "lost"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, index=True)
    type = Column(SAEnum(LeadType), nullable=False)
    source = Column(SAEnum(LeadSource), nullable=False)
    status = Column(SAEnum(LeadStatus), nullable=False, default=LeadStatus.new)
    customer_id = Column(String, ForeignKey("users.id"), nullable=True)
    employee_id = Column(String, ForeignKey("users.id"), nullable=True)
    zone_id = Column(String, ForeignKey("zones.id"), nullable=True)
    branch_id = Column(String, ForeignKey("branches.id"), nullable=True)
    farm_details = Column(Text, nullable=True)
    site_visit_date = Column(Date, nullable=True)
    advance_paid_date = Column(Date, nullable=True)
    won_date = Column(Date, nullable=True)
    lost_reason = Column(Text, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    customer = relationship("User", foreign_keys=[customer_id])
    employee = relationship("User", foreign_keys=[employee_id])
    zone = relationship("Zone", back_populates="leads")
    branch = relationship("Branch", foreign_keys=[branch_id])
