import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum, Float, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AgreementType(str, enum.Enum):
    one_time = "one_time"
    managed = "managed"
    lease = "lease"
    investment = "investment"


class AgreementStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class Agreement(Base):
    __tablename__ = "agreements"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    farm_id = Column(String, ForeignKey("farms.id"), nullable=True)
    type = Column(SAEnum(AgreementType), nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    payment_terms = Column(Text, nullable=True)
    amount = Column(Float, nullable=True)
    status = Column(SAEnum(AgreementStatus), nullable=False, default=AgreementStatus.draft)
    document_url = Column(String, nullable=True)  # Cloudinary URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    customer = relationship("Customer", back_populates="agreements")
    farm = relationship("Farm", back_populates="agreements")
