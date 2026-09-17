import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class WorkPartnerStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    blacklisted = "blacklisted"


class WorkPartner(Base):
    __tablename__ = "work_partners"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact = Column(String, nullable=True)
    zone_id = Column(String, ForeignKey("zones.id"), nullable=True)
    work_types = Column(JSON, nullable=True)      # list of WorkOrderType strings
    status = Column(SAEnum(WorkPartnerStatus), nullable=False, default=WorkPartnerStatus.active)
    payment_terms = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    zone = relationship("Zone", back_populates="work_partners")
    work_orders = relationship("WorkOrder", back_populates="outsourcing_partner")
