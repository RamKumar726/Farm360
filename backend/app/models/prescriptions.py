import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Float, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class PrescriptionStatus(str, enum.Enum):
    draft = "draft"
    sent = "sent"
    approved = "approved"
    rejected = "rejected"


class SentTo(str, enum.Enum):
    customer = "customer"
    admin = "admin"
    founder = "founder"
    employee = "employee"


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(String, primary_key=True, index=True)
    farm_id = Column(String, ForeignKey("farms.id"), nullable=False)
    agri_officer_id = Column(String, ForeignKey("users.id"), nullable=False)
    work_order_id = Column(String, ForeignKey("work_orders.id"), nullable=True)
    prescription_text = Column(Text, nullable=False)
    quote_amount = Column(Float, nullable=True)
    sent_to = Column(JSON, nullable=True)           # list of SentTo values
    status = Column(SAEnum(PrescriptionStatus), nullable=False, default=PrescriptionStatus.draft)
    attachment_url = Column(String, nullable=True)  # Cloudinary URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    farm = relationship("Farm", back_populates="prescriptions")
    agri_officer = relationship("User", foreign_keys=[agri_officer_id])
    work_order = relationship("WorkOrder", back_populates="prescriptions")
