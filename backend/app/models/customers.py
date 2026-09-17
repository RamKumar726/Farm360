import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ServiceType(str, enum.Enum):
    one_time = "one_time"
    managed = "managed"
    lease_outsourcing = "lease_outsourcing"
    lease_inhouse_complete = "lease_inhouse_complete"
    lease_inhouse_percentage = "lease_inhouse_percentage"
    lease_percentage_only = "lease_percentage_only"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    service_type = Column(SAEnum(ServiceType), nullable=True)
    branch_id = Column(String, ForeignKey("branches.id"), nullable=True)
    zone_id = Column(String, ForeignKey("zones.id"), nullable=True)
    subscription_active = Column(Boolean, default=False)
    subscription_start = Column(Date, nullable=True)
    subscription_end = Column(Date, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id])
    branch = relationship("Branch", foreign_keys=[branch_id])
    zone = relationship("Zone", foreign_keys=[zone_id])
    farms = relationship("Farm", back_populates="customer")
    agreements = relationship("Agreement", back_populates="customer")
    investments = relationship("Investment", back_populates="customer")
    land_sales = relationship("LandSale", back_populates="customer")
