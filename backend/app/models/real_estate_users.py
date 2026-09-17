import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class RegistrationStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class RealEstateUser(Base):
    __tablename__ = "real_estate_users"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    land_details = Column(Text, nullable=True)
    registration_status = Column(SAEnum(RegistrationStatus), nullable=False, default=RegistrationStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id])
    land_sales = relationship("LandSale", back_populates="real_estate_user")
